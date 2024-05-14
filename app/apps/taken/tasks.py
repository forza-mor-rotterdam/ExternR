import celery
from apps.meldingen.service import MeldingenService
from apps.taken.models import Taak
from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

DEFAULT_RETRY_DELAY = 2
MAX_RETRIES = 6

LOCK_EXPIRE = 5


class BaseTaskWithRetry(celery.Task):
    autoretry_for = (Exception,)
    max_retries = MAX_RETRIES
    default_retry_delay = DEFAULT_RETRY_DELAY


@shared_task(bind=True, base=BaseTaskWithRetry)
def compare_and_update_status(self, taak_id):
    taak = Taak.objects.get(id=taak_id)
    get_taakopdracht_response = MeldingenService().get_taakopdracht_data(
        taak.taakopdracht
    )
    if get_taakopdracht_response.status_code == 200:
        taakopdracht = get_taakopdracht_response.json()

        if taak.taakstatus.naam != taakopdracht.get("status").get("naam"):
            taakgebeurtenis = (
                taak.taakgebeurtenissen_voor_taak.filter(taakstatus=taak.taakstatus)
                .order_by("-aangemaakt_op")
                .first()
            )
            if taakgebeurtenis:
                update_data = {
                    "taakopdracht_url": taak.taakopdracht,
                    "status": {"naam": taak.taakstatus.naam},
                    "resolutie": taak.resolutie,
                    "omschrijving_intern": taakgebeurtenis.omschrijving_intern,
                    "gebruiker": taakgebeurtenis.gebruiker,
                    "bijlagen": [],
                }
                taak_status_aanpassen_response = (
                    MeldingenService().taak_status_aanpassen(
                        **update_data,
                    )
                )
                if taak_status_aanpassen_response.status_code != 200:
                    logger.error(
                        f"Celery compare and update status error, taak_status_aanpassen_response: status_code={taak_status_aanpassen_response.status_code}, taak_id={taak_id}, taakopdracht_id={taakopdracht.get('id')}, update_data={update_data}"
                    )
                    return {
                        "taak.id": taak_id,
                        "taakopdracht.id": taakopdracht.get("id"),
                        "taak_status_aanpassen_response.error_code": taak_status_aanpassen_response.status_code,
                    }

                else:
                    logger.warning(
                        f"Taakopdracht in Mor-Core updated successfully for ExternR taak_id: {taak_id} and MOR-Core taakopdracht_id: {taakopdracht.get('id')}."
                    )
                    return {
                        "taak.id": taak_id,
                        "taakopdracht.id": taakopdracht.get("id"),
                    }

    else:
        logger.error(
            f"Celery compare and update status error, get_taakopdracht_response: status_code={get_taakopdracht_response.status_code}, taak_id={taak_id}"
        )
        return {
            "taak.id": taak_id,
            "get_taakopdracht_response.error_code": get_taakopdracht_response.status_code,
        }
