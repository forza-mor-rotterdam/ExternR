import celery
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
def task_aanmaken_afbeelding_versies(self, bijlage_id):
    from apps.release_notes.models import Bijlage

    bijlage_instance = Bijlage.objects.get(id=bijlage_id)
    bijlage_instance.aanmaken_afbeelding_versies()
    bijlage_instance.save()

    return f"Bijlage id: {bijlage_instance.id}"
