from apps.meldingen.service import MeldingenService
from django import template
from django.contrib.auth import get_user_model
from utils.diversen import gebruikersnaam as gebruikersnaam_basis

register = template.Library()


@register.filter
def gebruikersnaam(value):
    return gebruikersnaam_basis(value)


@register.filter
def get_field_from_gebruiker_middels_email(value, field_name=None):
    # Leave field_name empty to return the name
    if not value:
        return ""

    gebruiker = get_gebruiker_object_middels_email(value)

    if field_name:
        return gebruiker.get(field_name, "")
    return gebruiker.get("full_name", "")


@register.filter
def get_gebruiker_object_middels_email(value):
    if not value:
        return None
    gebruiker_response = MeldingenService().get_gebruiker(
        gebruiker_email=value,
    )
    if gebruiker_response.status_code == 200:
        gebruiker = gebruiker_response.json()
        first_name = gebruiker.get("first_name", "")
        last_name = gebruiker.get("last_name", "")
        if full_name := f"{first_name} {last_name}".strip():
            gebruiker["full_name"] = full_name
    else:
        gebruiker = {}

    user_model = get_user_model()
    user_from_model = user_model.objects.filter(email=value).first()
    if user_from_model:
        gebruiker["rechtengroep"] = user_from_model.rechtengroep or ""
        gebruiker["rol"] = user_from_model.rol or ""
        if not gebruiker.get("first_name"):
            gebruiker["first_name"] = user_from_model.first_name or ""
        if not gebruiker.get("last_name"):
            gebruiker["last_name"] = user_from_model.last_name or ""
        if not gebruiker.get("email"):
            gebruiker["email"] = user_from_model.email or ""
        if not gebruiker.get("telefoonnummer"):
            gebruiker["telefoonnummer"] = user_from_model.telefoonnummer or ""
        if not gebruiker.get("full_name"):
            first_name = (
                user_from_model.first_name if user_from_model.first_name else ""
            )
            last_name = user_from_model.last_name if user_from_model.last_name else ""
            full_name = f"{first_name} {last_name}".strip()
            gebruiker["full_name"] = full_name or gebruiker["email"]

    return gebruiker


@register.filter
def get_taakgebeurtenis_voor_taakstatus(taak_gebeurtenissen, taakstatus):
    # Leave field_name empty to return the name
    if not taak_gebeurtenissen:
        return ""

    return taak_gebeurtenissen.filter(taakstatus__naam=taakstatus).first()


@register.filter
def get_laatste_taakgebeurtenis(taak_gebeurtenissen):
    if not taak_gebeurtenissen:
        return ""

    # Filter and order by creation date
    latest_taakgebeurtenis = (
        taak_gebeurtenissen.filter(
            taakstatus__naam__in=["voltooid", "voltooid_met_feedback"]
        )
        .order_by("-aangemaakt_op")
        .first()
    )

    return latest_taakgebeurtenis
