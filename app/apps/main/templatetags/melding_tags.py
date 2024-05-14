from apps.services.onderwerpen import render_onderwerp as render_onderwerp_service
from django import template

register = template.Library()


@register.filter
def taakopdracht(melding, taakopdracht_id):
    taakopdracht = {
        to.get("id"): to for to in melding.get("taakopdrachten_voor_melding", [])
    }.get(taakopdracht_id, {})
    return taakopdracht


@register.simple_tag
def render_onderwerp(onderwerp_url):
    return render_onderwerp_service(onderwerp_url)


@register.simple_tag
def get_bijlagen(melding):
    melding_bijlagen = [
        {
            **bijlage,
            "aangemaakt_op": melding.get("aangemaakt_op"),
            "label": "Foto van melder",
        }
        for bijlage in melding.get("bijlagen", [])
    ]
    signaal_bijlagen = [
        {
            **bijlage,
            "signaal": signaal,
            "aangemaakt_op": signaal.get("aangemaakt_op"),
            "label": f"Foto van melder ({signaal.get('bron_id')}): {signaal.get('bron_signaal_id')}",
        }
        for signaal in melding.get("signalen_voor_melding", [])
        for bijlage in signaal.get("bijlagen", [])
    ]
    meldinggebeurtenis_bijlagen = [
        {
            **bijlage,
            "meldinggebeurtenis": meldinggebeurtenis,
            "aangemaakt_op": meldinggebeurtenis.get("aangemaakt_op"),
            "label": "Foto van medewerker",
        }
        for meldinggebeurtenis in melding.get("meldinggebeurtenissen", [])
        for bijlage in meldinggebeurtenis.get("bijlagen", [])
    ]
    taakgebeurtenis_bijlagen = [
        {
            **bijlage,
            "taakgebeurtenis": meldinggebeurtenis.get("taakgebeurtenis", {}),
            "aangemaakt_op": meldinggebeurtenis.get("taakgebeurtenis", {}).get(
                "aangemaakt_op"
            ),
            "label": "Foto van medewerker",
        }
        for meldinggebeurtenis in melding.get("meldinggebeurtenissen", [])
        for bijlage in (
            meldinggebeurtenis.get("taakgebeurtenis", {}).get("bijlagen", [])
            if meldinggebeurtenis.get("taakgebeurtenis")
            else []
        )
    ]
    alle_bijlagen = (
        signaal_bijlagen
        + meldinggebeurtenis_bijlagen
        + taakgebeurtenis_bijlagen
        + melding_bijlagen
    )
    alle_bijlagen_gesorteerd = sorted(
        alle_bijlagen, key=lambda b: b.get("aangemaakt_op")
    )
    return alle_bijlagen_gesorteerd
