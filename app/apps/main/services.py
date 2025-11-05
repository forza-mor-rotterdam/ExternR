import logging

from apps.instellingen.models import Instelling
from django.conf import settings
from django.contrib import messages
from django.template.loader import get_template
from django.utils.safestring import mark_safe
from mor_api_services import MORCoreService as BasisMORCoreService
from mor_api_services import OnderwerpenService as BasisOnderwerpenService
from mor_api_services import PDOKService as BasisPDOKService
from mor_api_services import TaakRService as BasisTaakRService

logger = logging.getLogger(__name__)


def standaard_fout_afhandeling(service, response=None, fout=""):
    log = (
        f"API antwoord fout: {service.naar_json(response)}, status code: {response.status_code}"
        if not fout
        else f"Generiek fout: {fout}"
    )
    logger.error(log)

    message = (
        f'Er ging iets mis!: {service.naar_json(response).get("detail", "Geen detail gevonden")}, {service.__class__.__name__}[{response.status_code}]'
        if not fout
        else f"Er ging iets mis!: {service.__class__.__name__}"
    )
    if service._request:
        messages.error(service._request, message)

    return {
        "error": {
            "status_code": response.status_code if not fout else 500,
            "bericht": service.naar_json(response) if not fout else "",
        },
    }


class MORCoreService(BasisMORCoreService):
    def __init__(self, *args, **kwargs):
        instellingen = Instelling.actieve_instelling()
        kwargs.update(
            {
                "client_name": "ExternR",
                "basis_url": instellingen.mor_core_basis_url,
                "gebruikersnaam": instellingen.mor_core_gebruiker_email,
                "wachtwoord": instellingen.mor_core_gebruiker_wachtwoord,
                "token_timeout": instellingen.mor_core_token_timeout,
            }
        )
        super().__init__(*args, **kwargs)

    def met_fout(self, response=None, fout=""):
        return standaard_fout_afhandeling(self, response, fout)


class OnderwerpenService(BasisOnderwerpenService):
    def __init__(self, *args, **kwargs):
        instellingen = Instelling.actieve_instelling()
        kwargs.update(
            {
                "basis_url": instellingen.onderwerpen_basis_url,
            }
        )
        super().__init__(*args, **kwargs)

    def met_fout(self, response=None, fout=""):
        return standaard_fout_afhandeling(self, response, fout)


class TaakRService(BasisTaakRService):
    def __init__(self, *args, **kwargs):
        instellingen = Instelling.actieve_instelling()
        kwargs.update(
            {
                "basis_url": instellingen.taakr_basis_url,
            }
        )
        super().__init__(*args, **kwargs)

    def met_fout(self, response=None, fout=""):
        return standaard_fout_afhandeling(self, response, fout)


class PDOKService(BasisPDOKService):
    def __init__(self, *args, **kwargs):
        kwargs.update(
            {
                "gemeentecode": settings.WIJKEN_EN_BUURTEN_GEMEENTECODE,
                "basis_url": "https://api.pdok.nl",
                "api_pad": "bzk/locatieserver/search/v3_1",
                # "cache_timeout": 60 * 60 * 24 * 7,
            }
        )
        super().__init__(*args, **kwargs)

    def met_fout(self, response=None, fout=""):
        print(fout)
        # return standaard_fout_afhandeling(self, response, fout)


def render_onderwerp(onderwerp_url, standaard_naam=None, force_cache=False):
    onderwerp = OnderwerpenService().get_onderwerp(
        onderwerp_url, force_cache=force_cache
    )

    standaard_naam = onderwerp.get(
        "name", "Niet gevonden!" if not standaard_naam else standaard_naam
    )

    if onderwerp.get("priority") == "high":
        spoed_badge = get_template("badges/spoed.html")
        return mark_safe(f"{standaard_naam}{spoed_badge.render()}")
    return standaard_naam


def render_onderwerp_groepen(context, force_cache=False):
    try:
        groep_uuids = {}
        for key, value in context.items():
            onderwerp_url = value[0]
            onderwerp_data = OnderwerpenService().get_onderwerp(
                onderwerp_url,
                force_cache=force_cache,
            )
            onderwerp_group_uuid = onderwerp_data.get("group_uuid")
            groep_naam = (
                OnderwerpenService()
                .get_groep(
                    onderwerp_group_uuid,
                    force_cache=force_cache,
                )
                .get("name", "")
            )
            if onderwerp_group_uuid not in groep_uuids:
                groep_uuids[onderwerp_group_uuid] = {"naam": groep_naam, "items": []}

            groep_uuids[onderwerp_group_uuid]["items"].append(
                [
                    key,
                    {
                        "label": onderwerp_data.get("name", ""),
                        "item_count": value[1],
                    },
                ]
            )

        onderwerpen_gegroepeerd = [
            [info["naam"], sorted(info["items"], key=lambda b: b[1].get("label"))]
            for groep_uuid, info in groep_uuids.items()
        ]
        return sorted(onderwerpen_gegroepeerd, key=lambda x: x[0])
    except Exception as e:
        logger.error(f"Error onderwerp groep: {e}.")
    return None
