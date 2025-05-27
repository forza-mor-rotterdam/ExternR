import hashlib
import logging

from apps.instellingen.models import Instelling
from apps.main.services import PDOKService, TaakRService
from apps.taken.forms import (
    AfzenderEmailadresForm,
    TaakFeedbackHandleForm,
    TaaktypeAanmakenForm,
    TaaktypeAanpassenForm,
)
from apps.taken.models import AfzenderEmailadres, Taak, Taakstatus, Taaktype
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseServerError
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic.edit import CreateView, DeleteView, UpdateView
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
    def get_success_url(self):
        return reverse("taaktype_aanpassen", kwargs={"pk": self.object.id})


@method_decorator(login_required, name="dispatch")
@method_decorator(
    permission_required("authorisatie.taaktype_aanpassen", raise_exception=True),
    name="dispatch",
)
class TaaktypeAanpassenView(
    SuccessMessageMixin, TaaktypeAanmakenAanpassenView, UpdateView
):
    form_class = TaaktypeAanpassenForm
    success_message = "Het taaktype '%(omschrijving)s' is aangepast"

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
        taaktype_url = drf_reverse(
            "v1:taaktype-detail",
            kwargs={"uuid": self.object.uuid},
            request=self.request,
        )
        TaakRService().vernieuw_taaktypes(taaktype_url)
        if form.cleaned_data.get("redirect_field", "").startswith(
            instelling.taakr_basis_url
        ):
            return redirect(f"{form.cleaned_data.get('redirect_field')}{taaktype_url}")
        return response


@method_decorator(login_required, name="dispatch")
@method_decorator(
    permission_required("authorisatie.taaktype_aanmaken", raise_exception=True),
    name="dispatch",
)
class TaaktypeAanmakenView(
    SuccessMessageMixin, TaaktypeAanmakenAanpassenView, CreateView
):
    form_class = TaaktypeAanmakenForm
    success_message = "Het taaktype '%(omschrijving)s' is aangemaakt"

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
        taaktype_url = drf_reverse(
            "v1:taaktype-detail",
            kwargs={"uuid": self.object.uuid},
            request=self.request,
        )
        TaakRService().vernieuw_taaktypes(taaktype_url)
        if form.cleaned_data.get("redirect_field", "").startswith(
            instelling.taakr_basis_url
        ):
            return redirect(f"{form.cleaned_data.get('redirect_field')}{taaktype_url}")
        return response


def taak_feedback_handle(request, taak_id: int, email_hash: str):
    taak = get_object_or_404(Taak, pk=taak_id)
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
    if taak.resolutie == "niet_opgelost":
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
            taak = Taak.acties.status_aanpassen(
                taak=taak,
                status=Taakstatus.NaamOpties.VOLTOOID_MET_FEEDBACK,
                resolutie=Taak.ResolutieOpties.NIET_OPGELOST,
                omschrijving_intern=form.cleaned_data.get("omschrijving_intern"),
                gebruiker=taak.taaktype.externe_instantie_email,
                naar_niet_opgelost=True,
            )
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


class AfzenderEmailadresView(View):
    model = AfzenderEmailadres
    success_url = reverse_lazy("afzender_emailadres_lijst")


class AfzenderEmailadresLijstView(
    PermissionRequiredMixin, AfzenderEmailadresView, ListView
):
    queryset = AfzenderEmailadres.objects.order_by("email")
    permission_required = "authorisatie.afzender_emailadres_lijst_bekijken"


class AfzenderEmailadresAanmakenAanpassenView(AfzenderEmailadresView):
    def get_wijknamen(self):
        pdok_service = PDOKService()
        response = pdok_service.get_buurten_middels_gemeentecode()
        wijknamen = sorted(
            [wijk.get("wijknaam") for wijk in response.get("wijken", [])]
        )
        return wijknamen

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        afzender_emailadressen = AfzenderEmailadres.objects.all()
        if self.kwargs.get("pk"):
            afzender_emailadressen = AfzenderEmailadres.objects.exclude(
                id=self.get_object().id
            )

        gebruikte_wijknamen = list(
            set(
                [
                    wijk
                    for wijk_list in afzender_emailadressen.values_list(
                        "wijken", flat=True
                    )
                    for wijk in wijk_list
                ]
            )
        )
        kwargs.update(
            {
                "wijk_opties": [
                    (wijknaam, wijknaam)
                    for wijknaam in self.get_wijknamen()
                    if wijknaam not in gebruikte_wijknamen
                ]
            }
        )
        return kwargs

    # def get_success_url(self):
    #     return reverse("afzender_emailadres_aanpassen", kwargs={"pk": self.object.id})


class AfzenderEmailadresAanpassenView(
    PermissionRequiredMixin,
    SuccessMessageMixin,
    AfzenderEmailadresAanmakenAanpassenView,
    UpdateView,
):
    form_class = AfzenderEmailadresForm
    success_message = "Het afzender emailadres '%(email)s' is aangepast"
    permission_required = "authorisatie.afzender_emailadres_aanpassen"


class AfzenderEmailadresAanmakenView(
    PermissionRequiredMixin,
    SuccessMessageMixin,
    AfzenderEmailadresAanmakenAanpassenView,
    CreateView,
):
    form_class = AfzenderEmailadresForm
    success_message = "Het afzender emailadres '%(email)s' is aangemaakt"
    permission_required = "authorisatie.afzender_emailadres_aanmaken"


class AfzenderEmailadresVerwijderenView(
    PermissionRequiredMixin, AfzenderEmailadresView, DeleteView
):
    permission_required = "authorisatie.afzender_emailadres_verwijderen"

    def get(self, request, *args, **kwargs):
        object = self.get_object()
        response = self.delete(request, *args, **kwargs)
        messages.success(
            request, f"Het afzender emailadres '{object.email}' is verwijderd"
        )
        return response
