import json
import logging

import requests
from apps.context.filters import FilterManager
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
    to_base64,
)
from apps.meldingen.service import MeldingenService
from apps.services.onderwerpen import render_onderwerp
from apps.taken.models import Taak, Taakstatus, Taaktype
from device_detector import DeviceDetector
from django.conf import settings
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
from django.db.models import Q, Value
from django.db.models.functions import Concat
from django.http import HttpResponse, JsonResponse, StreamingHttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from rest_framework.reverse import reverse as drf_reverse

logger = logging.getLogger(__name__)


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

    filter_manager = FilterManager(taken, actieve_filters, foldout_states)

    taken_gefilterd = filter_manager.filter_taken()

    # request.session["taken_gefilterd"] = taken_gefilterd

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

    sortering = get_sortering(request.user)
    sort_reverse = len(sortering.split("-")) > 1
    sortering = sortering.split("-")[0]
    sorting_fields = {
        "Postcode": "taak_zoek_data__postcode",
        "Adres": "zoekadres",
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
    filter_manager = FilterManager(taken, actieve_filters)
    taken_gefilterd = filter_manager.filter_taken()

    # zoeken
    if request.session.get("q"):
        taken_gefilterd = taken_gefilterd.filter(
            Q(taak_zoek_data__straatnaam__iregex=request.session.get("q"))
            | Q(taak_zoek_data__huisnummer__iregex=request.session.get("q"))
            | Q(taak_zoek_data__bron_signaal_ids__icontains=request.session.get("q"))
        )

    # sorteren
    if sortering == "Adres":
        taken_gefilterd = taken_gefilterd.annotate(
            zoekadres=Concat(
                "taak_zoek_data__straatnaam",
                Value(" "),
                "taak_zoek_data__huisnummer",
                output_field=models.CharField(),
            )
        )
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
    if request.session.get("taken_gefilterd"):
        del request.session["taken_gefilterd"]

    return render(
        request,
        "taken/taken_lijst.html",
        {
            "taken": taken_paginated,
            "page_obj": page_obj,
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
    tijdlijn_data = melding_naar_tijdlijn(taak.melding.response_json)
    ua = request.META.get("HTTP_USER_AGENT")
    device = DeviceDetector(ua).parse()
    return render(
        request,
        "taken/taak_detail.html",
        {
            "id": id,
            "taak": taak,
            "tijdlijn_data": tijdlijn_data,
            "device_os": device.os_name().lower(),
        },
    )


@login_required
def onderwerp(request):
    url = request.GET.get("url")
    if not url:
        return http_404()

    onderwerp = render_onderwerp(request.GET.get("url"))
    return render(
        request,
        "onderwerpen/onderwerp.html",
        {
            "url": url,
            "onderwerp": onderwerp,
        },
    )


@user_passes_test(lambda u: u.is_superuser)
def clear_melding_token_from_cache(request):
    cache.delete("meldingen_token")
    return HttpResponse("melding_token removed from cache")


@login_required
@permission_required("authorisatie.taak_afronden", raise_exception=True)
def incident_modal_handle(request, id):
    context = request.user.profiel.context
    resolutie = request.GET.get("resolutie", "opgelost")
    taak = get_object_or_404(Taak, pk=id)

    # Alle taken voor deze melding
    openstaande_taken_voor_melding = Taak.objects.select_related(
        "melding",
        "taakstatus",
    ).filter(
        melding__response_json__id=taak.melding.response_json.get("id"),
        taakstatus__naam__in=Taakstatus.niet_voltooid_statussen(),
    )

    # Alle taaktype ids voor deze melding
    openstaande_taaktype_ids_voor_melding = list(
        {
            taaktype_id
            for taaktype_id in openstaande_taken_voor_melding.values_list(
                "taaktype__id", flat=True
            )
            .order_by("taaktype__id")
            .distinct()
        }
    )

    # Exclude alle taaktype ids voor vervolgtaken
    volgende_taaktypes = taak.taaktype.volgende_taaktypes.all().exclude(
        id__in=openstaande_taaktype_ids_voor_melding
    )

    form = TaakBehandelForm(
        volgende_taaktypes=volgende_taaktypes,
        initial={"resolutie": resolutie},
    )

    # Alle andere actieve /openstaande taken voor deze melding
    actieve_vervolg_taken = openstaande_taken_voor_melding.filter(
        taaktype__in=context.taaktypes.all(),
    ).exclude(
        id=taak.id,
    )
    if request.POST:
        form = TaakBehandelForm(
            request.POST,
            volgende_taaktypes=volgende_taaktypes,
            initial={"resolutie": resolutie},
        )
        if form.is_valid():
            # Afhandelen bijlagen
            bijlagen = request.FILES.getlist("bijlagen", [])
            bijlagen_base64 = []
            for f in bijlagen:
                file_name = default_storage.save(f.name, f)
                bijlagen_base64.append({"bestand": to_base64(file_name)})

            # Taak status aanpassen
            taak_status_aanpassen_response = MeldingenService().taak_status_aanpassen(
                taakopdracht_url=taak.taakopdracht,
                status="voltooid",
                resolutie=form.cleaned_data.get("resolutie"),
                omschrijving_intern=form.cleaned_data.get("omschrijving_intern"),
                bijlagen=bijlagen_base64,
                gebruiker=request.user.email,
            )
            if taak_status_aanpassen_response.status_code != 200:
                logger.error(
                    f"incident_modal_handle taak_status_aanpassen: status_code={taak_status_aanpassen_response.status_code}, taak_id={id}, repsonse_text={taak_status_aanpassen_response.text}"
                )

            # Aanmaken extra taken
            if (
                taak_status_aanpassen_response.status_code == 200
                and form.cleaned_data.get("nieuwe_taak")
            ):
                taken = form.cleaned_data.get("nieuwe_taak", [])
                for vervolg_taak in taken:
                    taaktype = Taaktype.objects.filter(id=vervolg_taak).first()
                    taaktype_url = (
                        drf_reverse(
                            "v1:taaktype-detail",
                            kwargs={"uuid": taaktype.uuid},
                            request=request,
                        )
                        if taaktype
                        else None
                    )

                    if taaktype_url:
                        taak_aanmaken_response = MeldingenService().taak_aanmaken(
                            melding_uuid=taak.melding.response_json.get("uuid"),
                            taaktype_url=taaktype_url,
                            titel=taaktype.omschrijving,
                            bericht=form.cleaned_data.get("omschrijving_nieuwe_taak"),
                            gebruiker=request.user.email,
                        )
                        if taak_aanmaken_response.status_code != 200:
                            logger.error(
                                f"incident_modal_handle taak_aanmaken: status code: {taak_aanmaken_response.status_code}, taak id: {id}, text: {taak_aanmaken_response.text}"
                            )
            return redirect("taken")
        else:
            logger.error(f"incident_modal_handle: for errors: {form.errors}")
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
    url = f"{settings.MELDINGEN_URL}{modified_path}"
    headers = {"Authorization": f"Token {MeldingenService().haal_token()}"}
    response = requests.get(url, stream=True, headers=headers)
    return StreamingHttpResponse(
        response.raw,
        content_type=response.headers.get("content-type"),
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
