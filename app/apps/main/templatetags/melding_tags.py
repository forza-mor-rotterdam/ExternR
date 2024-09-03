import logging

from apps.services.onderwerpen import render_onderwerp as render_onderwerp_service
from django import template

register = template.Library()
logger = logging.getLogger(__name__)


@register.filter
def taakopdracht(melding, taakopdracht_id):
    taakopdracht = {
        taakopdracht.get("id"): taakopdracht
        for taakopdracht in melding.get("taakopdrachten_voor_melding", [])
    }.get(taakopdracht_id, {})
    return taakopdracht


@register.simple_tag
def render_onderwerp(onderwerp_url):
    return render_onderwerp_service(onderwerp_url)


@register.simple_tag
def get_bijlagen(melding):
    # Initialize empty lists for different types of bijlagen
    melding_bijlagen = []
    signaal_bijlagen = []
    meldinggebeurtenis_bijlagen = []
    taakgebeurtenis_bijlagen = []

    # Process bijlagen if melding is a dictionary
    if isinstance(melding, dict):
        # Extract bijlagen from melding
        bijlagen = melding.get("bijlagen", [])

        # Process melding_bijlagen
        if isinstance(bijlagen, list):
            melding_bijlagen = [
                {
                    **bijlage,
                    "aangemaakt_op": melding.get("aangemaakt_op"),
                    "label": "Foto van melder",
                }
                for bijlage in bijlagen
            ]
        else:
            logger.error(f"No melding_bijlagen found or invalid format: {bijlagen}")

        # Process signaal_bijlagen
        for signaal in melding.get("signalen_voor_melding", []):
            bijlagen = signaal.get("bijlagen", [])
            if isinstance(bijlagen, list):
                signaal_bijlagen.extend(
                    [
                        {
                            **bijlage,
                            "signaal": signaal,
                            "aangemaakt_op": signaal.get("aangemaakt_op"),
                            "label": f"Foto van melder ({signaal.get('bron_id')}): {signaal.get('bron_signaal_id')}",
                        }
                        for bijlage in bijlagen
                    ]
                )
            else:
                logger.error(f"No signaal_bijlagen found or invalid format: {bijlagen}")

        # Process meldinggebeurtenis_bijlagen
        for meldinggebeurtenis in melding.get("meldinggebeurtenissen", []):
            bijlagen = meldinggebeurtenis.get("bijlagen", [])
            if isinstance(bijlagen, list):
                meldinggebeurtenis_bijlagen.extend(
                    [
                        {
                            **bijlage,
                            "meldinggebeurtenis": meldinggebeurtenis,
                            "aangemaakt_op": meldinggebeurtenis.get("aangemaakt_op"),
                            "label": "Foto van medewerker",
                        }
                        for bijlage in bijlagen
                    ]
                )
            else:
                logger.error(
                    f"No meldinggebeurtenis_bijlagen found or invalid format: {bijlagen}"
                )

        # Process taakgebeurtenis_bijlagen
        for meldinggebeurtenis in melding.get("meldinggebeurtenissen", []):
            taakgebeurtenis = meldinggebeurtenis.get("taakgebeurtenis")
            if taakgebeurtenis and isinstance(taakgebeurtenis, dict):
                bijlagen = taakgebeurtenis.get("bijlagen", [])
                if isinstance(bijlagen, list):
                    taakgebeurtenis_bijlagen.extend(
                        [
                            {
                                **bijlage,
                                "taakgebeurtenis": taakgebeurtenis,
                                "aangemaakt_op": taakgebeurtenis.get("aangemaakt_op"),
                                "label": "Foto van medewerker",
                            }
                            for bijlage in bijlagen
                        ]
                    )
                else:
                    logger.error(
                        f"No taakgebeurtenis_bijlagen found or invalid format: {bijlagen}"
                    )
            else:
                logger.error(
                    f"No taakgebeurtenis found or invalid format: {taakgebeurtenis}"
                )

    else:
        logger.error(f"Invalid melding object: {melding}")

    # Concatenate all bijlagen lists
    alle_bijlagen = (
        melding_bijlagen
        + signaal_bijlagen
        + meldinggebeurtenis_bijlagen
        + taakgebeurtenis_bijlagen
    )

    # Sort the combined bijlagen list by 'aangemaakt_op' field
    alle_bijlagen_gesorteerd = sorted(
        alle_bijlagen, key=lambda b: b.get("aangemaakt_op")
    )
    # Return the sorted list of bijlagen
    return alle_bijlagen_gesorteerd
