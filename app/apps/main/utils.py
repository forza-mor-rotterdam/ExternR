import base64

from django.core.files.storage import default_storage
from django.http import QueryDict
from utils.constanten import PDOK_WIJKEN


def get_filters(context):
    from apps.context.filters import FilterManager

    filters = context.filters.get("fields", [])
    filters = [f for f in filters if f in FilterManager.available_filter_names()]
    return filters


def get_actieve_filters(gebruiker, filters, status="nieuw"):
    actieve_filters = {f: [] for f in filters}
    profiel_filters = (
        gebruiker.profiel.filters.get(status, {})
        if isinstance(gebruiker.profiel.filters.get("status", {}), dict)
        else {}
    )
    actieve_filters.update({k: v for k, v in profiel_filters.items() if k in filters})
    return actieve_filters


def set_actieve_filters(gebruiker, actieve_filters, status="nieuw"):
    gebruiker.profiel.filters.update({status: actieve_filters})
    return gebruiker.profiel.save()


def get_sortering(gebruiker):
    return gebruiker.profiel.ui_instellingen.get("sortering", "Datum-reverse")


def set_sortering(gebruiker, nieuwe_sortering):
    gebruiker.profiel.ui_instellingen.update({"sortering": nieuwe_sortering})
    return gebruiker.profiel.save()


def get_kaart_modus(gebruiker):
    return gebruiker.profiel.ui_instellingen.get("kaart_modus", "volgen")


def set_kaart_modus(gebruiker, nieuwe_kaart_modus):
    gebruiker.profiel.ui_instellingen.update({"kaart_modus": nieuwe_kaart_modus})
    return gebruiker.profiel.save()


def dict_to_querystring(d: dict) -> str:
    return "&".join([f"{p}={v}" for p, l in d.items() for v in l])


def querystring_to_dict(s: str) -> dict:
    return dict(QueryDict(s))


def to_base64(file):
    binary_file = default_storage.open(file)
    binary_file_data = binary_file.read()
    base64_encoded_data = base64.b64encode(binary_file_data)
    base64_message = base64_encoded_data.decode("utf-8")
    return base64_message


def melding_naar_tijdlijn(melding: dict):
    tijdlijn_data = []
    t_ids = []
    row = []
    for mg in reversed(melding.get("meldinggebeurtenissen", [])):
        row = [0 for t in t_ids]

        tg = mg.get("taakgebeurtenis", {}) if mg.get("taakgebeurtenis", {}) else {}
        taakstatus_is_voltooid = (
            tg
            and tg.get("taakstatus")
            and tg.get("taakstatus", {}).get("naam") == "voltooid"
        )
        taakstatus_event = (
            tg
            and tg.get("taakstatus")
            and tg.get("taakstatus", {}).get("naam")
            in [
                "toegewezen",
                "openstaand",
            ]
            or tg
            and tg.get("gebeurtenis_type") == "gedeeld"
        )
        t_id = tg.get("taakopdracht")
        if t_id and t_id not in t_ids:
            try:
                i = t_ids.index(-1)
                t_ids[i] = t_id
                row[i] = 1
            except Exception:
                t_ids.append(t_id)
                row.append(1)

        if taakstatus_is_voltooid:
            index = t_ids.index(t_id)
            row[index] = 2
        if taakstatus_event:
            index = t_ids.index(t_id)
            row[index] = 3
        for i, t in enumerate(t_ids):
            row[i] = -1 if t == -1 else row[i]

        row.insert(0, 0 if tg else 1)

        if taakstatus_is_voltooid:
            index = t_ids.index(t_id)
            if index + 1 >= len(t_ids):
                del t_ids[-1]
            else:
                t_ids[index] = -1

        row_dict = {
            "mg": mg,
            "row": row,
        }
        tijdlijn_data.append(row_dict)

    row_dict = {
        "row": [t if t not in [1, 2, 3] else 0 for t in row],
    }
    tijdlijn_data.append(row_dict)
    tijdlijn_data = [t for t in reversed(tijdlijn_data)]
    return tijdlijn_data


def get_wijknaam_by_wijkcode(wijkcode):
    for wijk in PDOK_WIJKEN:
        if wijk["wijkcode"] == wijkcode:
            return wijk["wijknaam"]
    return None
