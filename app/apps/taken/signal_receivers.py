import logging

from apps.taken.managers import aangemaakt, gebeurtenis_toegevoegd, status_aangepast
from apps.taken.models import Taak
from apps.taken.tasks import task_taakopdracht_notificatie_voor_taak
from django.dispatch import receiver

logger = logging.getLogger(__name__)


@receiver(status_aangepast, dispatch_uid="taak_status_aangepast")
def status_aangepast_handler(sender, taak, status, vorige_status, *args, **kwargs):
    if kwargs.get("raw"):
        return
    logger.debug(f"status_aangepast_handler: {taak} - {vorige_status} -> {status}")
    get_taak = Taak.objects.get(id=taak.id)

    task_taakopdracht_notificatie_voor_taak.delay(
        taak_id=get_taak.id,
    )


@receiver(aangemaakt, dispatch_uid="taak_aangemaakt")
def aangemaakt_handler(sender, taak, *args, **kwargs):
    if kwargs.get("raw"):
        return
    logger.debug(f"aangemaakt_handler: {taak}")


@receiver(gebeurtenis_toegevoegd, dispatch_uid="gebeurtenis_toegevoegd")
def gebeurtenis_toegevoegd_handler(sender, taak, taakgebeurtenis, *args, **kwargs):
    if kwargs.get("raw"):
        return
    logger.debug(f"gebeurtenis_toegevoegd_handler: {taak}")
