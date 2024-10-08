import logging

from apps.taken.managers import aangemaakt, gebeurtenis_toegevoegd, status_aangepast
from apps.taken.models import Taak
from django.dispatch import receiver

logger = logging.getLogger(__name__)


@receiver(status_aangepast, dispatch_uid="taak_status_aangepast")
def status_aangepast_handler(sender, taak, status, vorige_status, *args, **kwargs):
    if kwargs.get("raw"):
        return
    logger.debug(f"status_aangepast_handler: {taak} - {vorige_status} -> {status}")
    get_taak = Taak.objects.get(id=taak.id)
    if get_taak.taakstatus.naam != status.naam:
        logger.error(
            f"compare taak status error: {get_taak.taakstatus.naam} == {status.naam}, taak={taak.id}, taakopdracht url={taak.taakopdracht}"
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
