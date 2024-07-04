import hashlib
import logging

from apps.instellingen.models import Instelling
from apps.meldingen.service import MeldingenService
from apps.taken.forms import (
    TaakFeedbackHandleForm,
    TaaktypeAanmakenForm,
    TaaktypeAanpassenForm,
)
from apps.taken.models import Taak, Taaktype
from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponseServerError
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from rest_framework.reverse import reverse as drf_reverse
from utils.diversen import absolute

logger = logging.getLogger(__name__)


@method_decorator(login_required, name="dispatch")
@method_decorator(
    permission_required("authorisatie.taaktype_bekijken", raise_exception=True),
    name="dispatch",
)
class TaaktypeView(View):
    model = Taaktype
    success_url = reverse_lazy("taaktype_lijst")


@method_decorator(login_required, name="dispatch")
@method_decorator(
    permission_required("authorisatie.taaktype_lijst_bekijken", raise_exception=True),
    name="dispatch",
)
class TaaktypeLijstView(TaaktypeView, ListView):
    ...


class TaaktypeAanmakenAanpassenView(TaaktypeView):
    ...


@method_decorator(login_required, name="dispatch")
@method_decorator(
    permission_required("authorisatie.taaktype_aanpassen", raise_exception=True),
    name="dispatch",
)
class TaaktypeAanpassenView(TaaktypeAanmakenAanpassenView, UpdateView):
    form_class = TaaktypeAanpassenForm

    def get_initial(self):
        instelling = Instelling.actieve_instelling()
        if not instelling:
            raise Exception(
                "De TaakR url kan niet worden gevonden, Er zijn nog geen instellingen aangemaakt"
            )

        initial = self.initial.copy()
        initial["redirect_field"] = (
            self.request.GET.get("redirect_url", "")
            if self.request.GET.get("redirect_url", "").startswith(
                instelling.taakr_basis_url
            )
            else None
        )
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["taaktype_url"] = drf_reverse(
            "v1:taaktype-detail",
            kwargs={"uuid": self.object.uuid},
            request=self.request,
        )
        return context

    def form_valid(self, form):
        instelling = Instelling.actieve_instelling()
        if not instelling:
            raise Exception(
                "De TaakR url kan niet worden gevonden, Er zijn nog geen instellingen aangemaakt"
            )

        response = super().form_valid(form)
        if form.cleaned_data.get("redirect_field", "").startswith(
            instelling.taakr_basis_url
        ):
            taaktype_url = drf_reverse(
                "v1:taaktype-detail",
                kwargs={"uuid": self.object.uuid},
                request=self.request,
            )
            return redirect(f"{form.cleaned_data.get('redirect_field')}{taaktype_url}")
        return response


@method_decorator(login_required, name="dispatch")
@method_decorator(
    permission_required("authorisatie.taaktype_aanmaken", raise_exception=True),
    name="dispatch",
)
class TaaktypeAanmakenView(TaaktypeAanmakenAanpassenView, CreateView):
    form_class = TaaktypeAanmakenForm

    def get(self, request, *args, **kwargs):
        taaktype_url = request.GET.get("taaktype_url", "")
        if taaktype_url.startswith(absolute(request).get("ABSOLUTE_ROOT")):
            taaktype_uuid = taaktype_url.split("/")[-2]
            taaktype = Taaktype.objects.filter(uuid=taaktype_uuid).first()
            if taaktype:
                return redirect(reverse("taaktype_aanpassen", args=[taaktype.id]))
        return super().get(request, *args, **kwargs)

    def get_initial(self):
        instelling = Instelling.actieve_instelling()
        if not instelling:
            raise Exception(
                "De TaakR url kan niet worden gevonden, Er zijn nog geen instellingen aangemaakt"
            )

        initial = self.initial.copy()
        initial["redirect_field"] = (
            self.request.GET.get("redirect_url", "")
            if self.request.GET.get("redirect_url", "").startswith(
                instelling.taakr_basis_url
            )
            else None
        )
        return initial

    def form_valid(self, form):
        instelling = Instelling.actieve_instelling()
        if not instelling:
            raise Exception(
                "De TaakR url kan niet worden gevonden, Er zijn nog geen instellingen aangemaakt"
            )

        response = super().form_valid(form)
        if form.cleaned_data.get("redirect_field", "").startswith(
            instelling.taakr_basis_url
        ):
            taaktype_url = drf_reverse(
                "v1:taaktype-detail",
                kwargs={"uuid": self.object.uuid},
                request=self.request,
            )
            return redirect(f"{form.cleaned_data.get('redirect_field')}{taaktype_url}")
        return response


def taak_feedback_handle(request, taak_id: int, email_hash: str):
    taak = get_object_or_404(Taak, pk=taak_id)
    taakgebeurtenis = (
        taak.taakgebeurtenissen_voor_taak.filter(taakstatus=taak.taakstatus)
        .order_by("-aangemaakt_op")
        .first()
    )
    form = None
    try:
        verwachte_hash = hashlib.sha256(
            (str(taak_id) + settings.SECRET_HASH_KEY).encode()
        ).hexdigest()
        if verwachte_hash != email_hash:
            logger.error("Feedback hashes don't match")
            return HttpResponseServerError(
                "De hash komt niet overeen met de verwachte waarde.",
                status=500,
            )
    except Exception as e:
        # Afhandelen onverwachte errors
        logger.error(f"An error occurred: {str(e)}")
        return HttpResponseServerError(
            "Er is een fout opgetreden bij het verwerken van uw verzoek.",
            status=500,
        )
    # Taak is eerder veranderd naar niet_opgelost
    if taakgebeurtenis.resolutie == "niet_opgelost":
        return render(
            request,
            "taken/taak_externe_instantie_eerder_voltooid.html",
            {
                "taak": taak,
            },
        )
    # Feedback niet opgelost
    form = TaakFeedbackHandleForm()
    if request.POST:
        form = TaakFeedbackHandleForm(request.POST)
        if form.is_valid():
            taak_status_aanpassen_response = MeldingenService().taak_status_aanpassen(
                taakopdracht_url=taak.taakopdracht,
                status="voltooid",
                resolutie="niet_opgelost",
                omschrijving_intern=form.cleaned_data.get("omschrijving_intern"),
                gebruiker=taak.taaktype.externe_instantie_email,
            )
            if taak_status_aanpassen_response.status_code != 200:
                logger.error(
                    f"taak_feedback_handle taak_status_aanpassen: status_code={taak_status_aanpassen_response.status_code}, taak_id={id}, repsonse_text={taak_status_aanpassen_response.text}"
                )
            if taak_status_aanpassen_response.status_code == 200:
                return render(
                    request,
                    "taken/taak_externe_instantie_bedankt.html",
                    {
                        "taak": taak,
                    },
                )
    return render(
        request,
        "taken/taak_externe_instantie_feedback.html",
        {
            "form": form,
            "taak": taak,
        },
    )
