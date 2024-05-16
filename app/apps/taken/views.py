import hashlib
import logging

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
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView

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

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        current_taaktype = self.get_object()
        kwargs["current_taaktype"] = current_taaktype
        return kwargs


@method_decorator(login_required, name="dispatch")
@method_decorator(
    permission_required("authorisatie.taaktype_aanmaken", raise_exception=True),
    name="dispatch",
)
class TaaktypeAanmakenView(TaaktypeAanmakenAanpassenView, CreateView):
    form_class = TaaktypeAanmakenForm


def taak_feedback_handle(
    request, taak_id: int, email_hash: str, email_feedback_type: int
):
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
    # Geen valide feedback_type (opgelost of niet_opgelost)
    if email_feedback_type not in [0, 1]:
        logger.error(f"Incorrect value for email_feedback_type: {email_feedback_type}")
        return HttpResponseServerError(
            f"Ongeldige waarde voor email_feedback_type: {email_feedback_type}.",
            status=500,
        )
    # Taak is reeds voltooid
    if taak.taakstatus.naam == "voltooid":
        return render(
            request,
            "taken/taak_externe_instantie_eerder_voltooid.html",
            {
                "taak": taak,
            },
        )
    # Feedback niet opgelost
    if email_feedback_type == 0:
        form = TaakFeedbackHandleForm()
        if request.POST:
            form = TaakFeedbackHandleForm(request.POST)
            if form.is_valid():
                taak_status_aanpassen_response = (
                    MeldingenService().taak_status_aanpassen(
                        taakopdracht_url=taak.taakopdracht,
                        status="voltooid",
                        resolutie="niet_opgelost",
                        omschrijving_intern=form.cleaned_data.get(
                            "omschrijving_intern"
                        ),
                        gebruiker=taak.taaktype.externe_instantie_email,
                    )
                )
                if taak_status_aanpassen_response.status_code != 200:
                    logger.error(
                        f"taak_toewijzing_intrekken taak_status_aanpassen: status_code={taak_status_aanpassen_response.status_code}, taak_id={id}, repsonse_text={taak_status_aanpassen_response.text}"
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
    # Feedback opgelost
    elif email_feedback_type == 1:
        taak_status_aanpassen_response = MeldingenService().taak_status_aanpassen(
            taakopdracht_url=taak.taakopdracht,
            status="voltooid",
            resolutie="opgelost",
            gebruiker=taak.taaktype.externe_instantie_email,
        )
        if taak_status_aanpassen_response.status_code != 200:
            logger.error(
                f"taak_toewijzing_intrekken taak_status_aanpassen: status_code={taak_status_aanpassen_response.status_code}, taak_id={id}, repsonse_text={taak_status_aanpassen_response.text}"
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
        "taken/taak_externe_instantie_bedankt.html",
        {
            "taak": taak,
        },
    )
