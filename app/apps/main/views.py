import json
import logging
import operator
from functools import reduce

import requests
from apps.context.filters import FilterManager
from apps.instellingen.models import Instelling
from apps.main.forms import KaartModusForm, SorteerFilterForm, TaakBehandelForm
from apps.main.utils import (
    get_actieve_filters,
    get_filters,
    get_kaart_modus,
    get_sortering,
    melding_naar_tijdlijn,
    set_actieve_filters,
    set_kaart_modus,
    set_sortering,
)
from apps.meldingen.service import MeldingenService
from apps.services.pdok import PDOKService
from apps.services.taakr import TaakRService
from apps.taken.models import Taak
from apps.taken.tasks import task_taak_status_voltooid
from device_detector import DeviceDetector
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import (
    login_required,
    permission_required,
    user_passes_test,
)
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.core import signing
from django.core.cache import cache
from django.core.files.storage import default_storage
from django.core.paginator import Paginator
from django.db import models
from django.db.models import Case, F, Q, Value, When
from django.db.models.functions import Cast, Concat
from django.http import HttpResponse, JsonResponse, StreamingHttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

logger = logging.getLogger(__name__)


@login_required
def wijken_en_buurten(request):
    service = PDOKService()
    response = service.get_buurten_middels_gemeentecode(
        request.GET.get("gemeentecode", settings.WIJKEN_EN_BUURTEN_GEMEENTECODE)
    )
    return JsonResponse(response)


def http_403(request):
    return render(
        request,
        "403.html",
    )


def http_404(request):
    return render(
        request,
        "404.html",
    )


def http_500(request):
    return render(
        request,
        "500.html",
    )


def informatie(request):
    return render(
        request,
        "auth/informatie.html",
        {},
    )


# Verander hier de instellingen voor de nieuwe homepagina.
def root(request):
    if request.user.is_authenticated:
        if request.user.has_perms(["authorisatie.taken_lijst_bekijken"]):
            return redirect(reverse("taken"), False)
        if request.user.has_perms(["authorisatie.beheer_bekijken"]):
            return redirect(reverse("beheer"), False)
        return render(
            request,
            "home_ingelogd.html",
            {},
        )
    return render(
        request,
        "home.html",
        {},
    )


@login_required
def ui_settings_handler(request):
    profiel = request.user.profiel
    if request.POST:
        profiel.ui_instellingen.update(
            {"fontsize": request.POST.get("fontsize", "fz-medium")}
        )
        profiel.save()

    return render(
        request,
        "snippets/form_pageheader.html",
        {"profile": profiel},
    )


@login_required
@permission_required("authorisatie.taken_lijst_bekijken", raise_exception=True)
def taken(request):
    MeldingenService().set_gebruiker(
        gebruiker=request.user.serialized_instance(),
    )
    return render(
        request,
        "taken/taken.html",
        {},
    )


@login_required
@permission_required("authorisatie.taken_lijst_bekijken", raise_exception=True)
def taken_filter(request):
    taken = Taak.objects.select_related(
        "melding",
        "taakstatus",
        "taak_zoek_data",
    ).get_taken_recent(request.user)

    filters = (
        get_filters(request.user.profiel.context)
        if request.user.profiel.context
        else []
    )
    filters += ["q"]
    actieve_filters = get_actieve_filters(request.user, filters)
    actieve_filters["q"] = request.session.get("q", [""])
    foldout_states = []

    if request.POST:
        request_filters = {f: request.POST.getlist(f) for f in filters}
        foldout_states = json.loads(request.POST.get("foldout_states", "[]"))
        for filter_name, new_value in request_filters.items():
            if filter_name != "q" and new_value != actieve_filters.get(filter_name):
                actieve_filters[filter_name] = new_value
        set_actieve_filters(request.user, actieve_filters)

    filter_manager = FilterManager(
        taken, actieve_filters, foldout_states, profiel=request.user.profiel
    )

    taken_gefilterd = filter_manager.filter_taken()

    taken_gefilterd = taken_gefilterd.annotate(
        huisnr_huisltr_toev=Concat(
            Cast(F("taak_zoek_data__huisnummer"), output_field=models.CharField()),
            "taak_zoek_data__huisletter",
            Case(
                When(
                    Q(taak_zoek_data__toevoeging__isnull=False)
                    & ~Q(taak_zoek_data__toevoeging=""),
                    then=Concat(
                        Value("-"),
                        "taak_zoek_data__toevoeging",
                    ),
                )
            ),
        )
    )
    taken_gefilterd = taken_gefilterd.annotate(
        adres=Concat(
            "taak_zoek_data__straatnaam",
            Value(" "),
            "huisnr_huisltr_toev",
        )
    )
    # zoeken
    if request.session.get("q"):
        q = [qp.strip() for qp in request.session.get("q").split(" ") if qp.strip(" ")]
        q_list = [
            Q(taak_zoek_data__bron_signaal_ids__icontains=qp)
            | Q(taak_zoek_data__straatnaam__iregex=qp)
            | Q(taak_zoek_data__huisnummer__iregex=qp)
            if len(qp) > 3
            else Q(taak_zoek_data__straatnaam__iregex=qp)
            | Q(taak_zoek_data__huisnummer__iregex=qp)
            for qp in q
        ]
        taken_gefilterd = taken_gefilterd.filter(reduce(operator.and_, q_list))

    taken_aantal = taken_gefilterd.count()
    return render(
        request,
        "taken/taken_filter_form.html",
        {
            "taken_aantal": taken_aantal,
            "filter_manager": filter_manager,
            "foldout_states": json.dumps(foldout_states),
        },
    )


@login_required
@permission_required("authorisatie.taken_lijst_bekijken", raise_exception=True)
def taken_lijst(request):
    try:
        pnt = Point(
            float(request.GET.get("lon", 0)),
            float(request.GET.get("lat", 0)),
            srid=4326,
        )
    except Exception:
        pnt = Point(0, 0, srid=4326)

    if request.GET.get("toon_alle_taken"):
        request.session["toon_alle_taken"] = True

    sortering = get_sortering(request.user)
    sort_reverse = len(sortering.split("-")) > 1
    sortering = sortering.split("-")[0]
    sorting_fields = {
        "Postcode": "taak_zoek_data__postcode",
        "Adres": "adres",
        "Datum": "taakstatus__aangemaakt_op",
        "Afstand": "afstand",
    }

    # filteren
    taken = Taak.objects.select_related(
        "melding",
        "taakstatus",
        "taak_zoek_data",
    ).get_taken_recent(request.user)
    filters = (
        get_filters(request.user.profiel.context)
        if request.user.profiel.context
        else []
    )
    actieve_filters = get_actieve_filters(request.user, filters)
    filter_manager = FilterManager(taken, actieve_filters, profiel=request.user.profiel)
    taken_gefilterd = filter_manager.filter_taken()

    taken_gefilterd = taken_gefilterd.annotate(
        huisnr_huisltr_toev=Concat(
            Cast(F("taak_zoek_data__huisnummer"), output_field=models.CharField()),
            "taak_zoek_data__huisletter",
            Case(
                When(
                    Q(taak_zoek_data__toevoeging__isnull=False)
                    & ~Q(taak_zoek_data__toevoeging=""),
                    then=Concat(
                        Value("-"),
                        "taak_zoek_data__toevoeging",
                    ),
                )
            ),
        )
    )
    taken_gefilterd = taken_gefilterd.annotate(
        adres=Concat(
            "taak_zoek_data__straatnaam",
            Value(" "),
            "huisnr_huisltr_toev",
        )
    )
    # zoeken
    if request.session.get("q"):
        q = [qp.strip() for qp in request.session.get("q").split(" ") if qp.strip(" ")]
        q_list = [
            Q(taak_zoek_data__bron_signaal_ids__icontains=qp)
            | Q(taak_zoek_data__straatnaam__iregex=qp)
            | Q(taak_zoek_data__huisnummer__iregex=qp)
            if len(qp) > 3
            else Q(taak_zoek_data__straatnaam__iregex=qp)
            | Q(taak_zoek_data__huisnummer__iregex=qp)
            for qp in q
        ]
        taken_gefilterd = taken_gefilterd.filter(reduce(operator.and_, q_list))

    if sortering == "Afstand":
        taken_gefilterd = taken_gefilterd.annotate(
            afstand=Distance("taak_zoek_data__geometrie", pnt)
        )
    taken_gefilterd = taken_gefilterd.order_by(
        f"{'-' if sort_reverse else ''}{sorting_fields.get(sortering)}"
    )

    # paginate
    # @Remco @TODO Set to 5 for easier testing
    paginator = Paginator(taken_gefilterd, 50)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    taken_paginated = page_obj.object_list
    taken_gefilterd_total = taken_gefilterd.count()
    if request.session.get("taken_gefilterd"):
        del request.session["taken_gefilterd"]

    return render(
        request,
        "taken/taken_lijst.html",
        {
            "taken_gefilterd_total": taken_gefilterd_total,
            "taken": taken_paginated,
            "page_obj": page_obj,
            "toon_alle_taken": request.session.get("toon_alle_taken", False),
        },
    )


@login_required
@permission_required("authorisatie.taken_lijst_bekijken", raise_exception=True)
def taak_zoeken(request):
    body = json.loads(request.body)
    request.session["q"] = body.get("q", "")
    return JsonResponse({"q": request.session.get("q", "")})


@login_required
def sorteer_filter(request):
    sortering = get_sortering(request.user)
    form = SorteerFilterForm({"sorteer_opties": sortering})
    request_type = "get"
    if request.POST:
        request_type = "post"
        form = SorteerFilterForm(request.POST)
        if form.is_valid():
            sortering = form.cleaned_data.get("sorteer_opties")
            set_sortering(request.user, sortering)
    return render(
        request,
        "snippets/sorteer_filter_form.html",
        {
            "form": form,
            "request_type": request_type,
        },
    )


@login_required
def kaart_modus(request):
    kaart_modus = get_kaart_modus(request.user)
    form = KaartModusForm({"kaart_modus": kaart_modus})
    request_type = "get"
    if request.POST:
        request_type = "post"
        form = KaartModusForm(request.POST, {"kaart_modus": kaart_modus})
        if form.is_valid():
            kaart_modus = form.cleaned_data.get("kaart_modus")
            set_kaart_modus(request.user, kaart_modus)
    return render(
        request,
        "snippets/kaart_modus_form.html",
        {
            "form": form,
            "request_type": request_type,
        },
    )


@login_required
@permission_required("authorisatie.taak_bekijken", raise_exception=True)
def taak_detail(request, id):
    taak = get_object_or_404(Taak, pk=id)
    ua = request.META.get("HTTP_USER_AGENT", "")
    device = DeviceDetector(ua).parse()
    return render(
        request,
        "taken/taak_detail.html",
        {
            "id": id,
            "taak": taak,
            "device_os": device.os_name().lower(),
        },
    )


@login_required
@permission_required("authorisatie.taak_bekijken", raise_exception=True)
def taak_detail_melding_tijdlijn(request, id):
    taak = get_object_or_404(Taak, pk=id)
    tijdlijn_data = melding_naar_tijdlijn(taak.melding.response_json)

    return render(
        request,
        "taken/taak_detail_melding_tijdlijn.html",
        {
            "id": id,
            "taak": taak,
            "tijdlijn_data": tijdlijn_data,
        },
    )


@user_passes_test(lambda u: u.is_superuser)
def clear_melding_token_from_cache(request):
    cache.delete("meldingen_token")
    return HttpResponse("melding_token removed from cache")


@login_required
@permission_required("authorisatie.taak_afronden", raise_exception=True)
def taak_afhandelen(request, id):
    resolutie = request.GET.get("resolutie", "opgelost")
    taak = get_object_or_404(Taak, pk=id)
    taaktypes = TaakRService().get_taaktypes(
        params={
            "taakapplicatie_taaktype_url": taak.taaktype.taaktype_url(request),
        },
        force_cache=True,
    )
    volgende_taaktypes = []
    actieve_vervolg_taken = []
    if taak.taakstatus.naam in ["voltooid", "voltooid_met_feedback"]:
        messages.warning(request, "Deze taak is ondertussen al afgerond.")
        return render(
            request,
            "incident/modal_handle.html",
            {
                "taak": taak,
            },
        )
    if not taaktypes:
        messages.error(
            request,
            f"Vervolg taaktypes voor taaktype '{taak.taaktype.omschrijving}' konden niet worden opgehaald.",
        )

    if taaktypes:
        openstaande_taaktype_urls_voor_melding = [
            taakopdracht.get("taaktype")
            for taakopdracht in taak.melding.response_json.get(
                "taakopdrachten_voor_melding", []
            )
            if taakopdracht.get("status", {}).get("naam") == "nieuw"
        ]
        alle_volgende_taaktypes = [
            (
                TaakRService()
                .get_taaktype_by_url(taaktype_url)
                .get("taakapplicatie_taaktype_url"),
                TaakRService().get_taaktype_by_url(taaktype_url).get("omschrijving"),
            )
            for taaktype_url in taaktypes[0].get("volgende_taaktypes", [])
        ]
        volgende_taaktypes = [
            taaktype
            for taaktype in alle_volgende_taaktypes
            if taaktype[0] not in openstaande_taaktype_urls_voor_melding
        ]
        actieve_vervolg_taken = [
            taaktype
            for taaktype in alle_volgende_taaktypes
            if taaktype[0] in openstaande_taaktype_urls_voor_melding
        ]

    form = TaakBehandelForm(
        volgende_taaktypes=volgende_taaktypes,
        initial={"resolutie": resolutie},
    )

    if request.POST:
        form = TaakBehandelForm(
            request.POST,
            request.FILES,
            volgende_taaktypes=volgende_taaktypes,
            initial={"resolutie": resolutie},
        )
        if form.is_valid():
            volgende_taaktypes_lookup = {
                taaktype[0]: taaktype[1] for taaktype in volgende_taaktypes
            }
            vervolg_taaktypes = [
                {
                    "taaktype_url": taaktype_url,
                    "omschrijving": volgende_taaktypes_lookup.get(taaktype_url),
                }
                for taaktype_url in form.cleaned_data.get("nieuwe_taak", [])
            ]

            bijlagen = request.FILES.getlist("bijlagen", [])
            bijlage_paded = []
            for f in bijlagen:
                file_name = default_storage.save(f.name, f)
                bijlage_paded.append(file_name)

            task_taak_status_voltooid.delay(
                taak_id=taak.id,
                gebruiker_email=request.user.email,
                resolutie=form.cleaned_data.get("resolutie"),
                omschrijving_intern=form.cleaned_data.get("omschrijving_intern"),
                bijlage_paden=bijlage_paded,
                vervolg_taaktypes=vervolg_taaktypes,
                vervolg_taak_bericht=form.cleaned_data.get("omschrijving_nieuwe_taak"),
            )
            return redirect("taken")
        else:
            logger.error(f"taak_afhandelen: for errors: {form.errors}")

    return render(
        request,
        "incident/modal_handle.html",
        {
            "taak": taak,
            "form": form,
            "actieve_vervolg_taken": actieve_vervolg_taken,
        },
    )


@login_required
def config(request):
    return render(
        request,
        "config.html",
    )


def _meldingen_bestand(request, modified_path):
    instelling = Instelling.actieve_instelling()
    if not instelling:
        raise Exception(
            "De MOR-Core url kan niet worden gevonden, Er zijn nog geen instellingen aangemaakt"
        )
    url = f"{instelling.mor_core_basis_url}{modified_path}"
    response = requests.get(url, stream=True, headers=MeldingenService().get_headers())
    return StreamingHttpResponse(
        response.raw,
        content_type=response.headers.get("content-type"),
        headers={
            "Content-Disposition": "inline",
        },
        status=response.status_code,
        reason=response.reason,
    )


def meldingen_bestand(request):
    modified_path = request.path.replace(settings.MOR_CORE_URL_PREFIX, "")
    if request.GET.get("signed-data"):
        try:
            signing.loads(
                request.GET.get("signed-data"),
                max_age=settings.SIGNED_DATA_MAX_AGE_SECONDS,
                salt=settings.SECRET_KEY,
            )
            return _meldingen_bestand(request, modified_path)
        except signing.BadSignature:
            ...
    return meldingen_bestand_protected(request)


@login_required
@permission_required("authorisatie.taak_bekijken", raise_exception=True)
def meldingen_bestand_protected(request):
    modified_path = request.path.replace(settings.MOR_CORE_PROTECTED_URL_PREFIX, "")
    return _meldingen_bestand(request, modified_path)
