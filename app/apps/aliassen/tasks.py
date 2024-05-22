from datetime import timedelta

import celery
from celery import shared_task
from celery.utils.log import get_task_logger
from django.utils import timezone

logger = get_task_logger(__name__)

DEFAULT_RETRY_DELAY = 2
MAX_RETRIES = 6

LOCK_EXPIRE = 5


class BaseTaskWithRetry(celery.Task):
    autoretry_for = (Exception,)
    max_retries = MAX_RETRIES
    default_retry_delay = DEFAULT_RETRY_DELAY


@shared_task(bind=True, base=BaseTaskWithRetry)
def task_maak_bijlagealias(self, bijlage_url, taakgebeurtenis_id):
    from apps.aliassen.models import BijlageAlias
    from apps.taken.models import Taakgebeurtenis

    bijlage_instance = BijlageAlias.objects.create(
        bron_url=bijlage_url,
        taak_gebeurtenis=Taakgebeurtenis.objects.get(pk=taakgebeurtenis_id),
    )

    return f"BijlageAlias id: {bijlage_instance.pk}"


@shared_task(bind=True, base=BaseTaskWithRetry)
def task_update_melding_alias_data_for_all_meldingen(self, cache_timeout=0):
    from apps.aliassen.models import MeldingAlias

    if not isinstance(cache_timeout, int):
        cache_timeout = 0

    datetime_to_update = timezone.now() - timedelta(seconds=cache_timeout)
    all_melding_alias_items = MeldingAlias.objects.all()
    melding_alias_items_for_update = all_melding_alias_items.filter(
        aangepast_op__lte=datetime_to_update
    )
    for melding_alias in melding_alias_items_for_update:
        melding_alias.valideer_bron_url()
        melding_alias.save()
        melding_alias.update_zoek_data()

    return f"updated/totaal={melding_alias_items_for_update.count()}/{all_melding_alias_items.count()}"


@shared_task(bind=True, base=BaseTaskWithRetry)
def task_update_melding_alias_data(self, melding_alias_id):
    from apps.aliassen.models import MeldingAlias

    melding_alias = MeldingAlias.objects.filter(pk=melding_alias_id).first()
    if melding_alias:
        melding_alias.valideer_bron_url()
        melding_alias.update_zoek_data()
        melding_alias.save()
    else:
        raise ValueError(
            f"No melding alias found for melding_alias_id: {melding_alias_id}"
        )

    return f"MeldingAlias with id={melding_alias_id}, updated"


@shared_task(bind=True, base=BaseTaskWithRetry)
def task_vind_en_fix_meldingalias_duplicaten(self):
    from apps.aliassen.models import MeldingAlias
    from apps.taken.models import Taak
    from django.db.models import Count

    mas = (
        MeldingAlias.objects.values("bron_url")
        .annotate(Count("id"))
        .order_by()
        .filter(id__count__gt=1)
    )
    urls = [ms.get("bron_url") for ms in mas]
    logger.info("urls")
    logger.info(urls)
    for url in urls:
        melding_alias = MeldingAlias.objects.filter(bron_url=url).first()
        logger.info("melding_alias")
        logger.info(melding_alias)
        taken = [taak for taak in Taak.objects.filter(melding__bron_url=url)]
        logger.info("taken")
        logger.info(taken)
        for taak in taken:
            logger.info("taak")
            logger.info(taak.melding.id)
            taak.melding = melding_alias
        Taak.objects.bulk_update(taken, fields=["melding"])

    melding_alias_to_be_deleted = MeldingAlias.objects.annotate(
        taken_count=Count("taken_voor_meldingalias")
    ).filter(
        taken_count=0,
        bron_url__in=urls,
    )
    deleted_melding_alias_ids = [
        str(id) for id in list(melding_alias_to_be_deleted.values_list("id", flat=True))
    ]
    logger.info("deleted_melding_alias_ids")
    logger.info(deleted_melding_alias_ids)
    melding_alias_deleted = MeldingAlias.objects.filter(
        id__in=deleted_melding_alias_ids
    ).delete()
    logger.info("melding_alias_deleted")
    logger.info(melding_alias_deleted)

    return f"Dubbele MeldingAlias: aantal={len(urls)}, bron_urls={', '.join(urls)}, verwijderde MeldingAlias ids={', '.join(deleted_melding_alias_ids)}"


@shared_task(bind=True, base=BaseTaskWithRetry)
def task_vind_meldingalias_duplicaten(self):
    from apps.aliassen.models import MeldingAlias
    from django.db.models import Count

    mas = (
        MeldingAlias.objects.values("bron_url")
        .annotate(Count("id"))
        .order_by()
        .filter(id__count__gt=1)
    )
    urls = [ms.get("bron_url") for ms in mas]
    return f"Dubbele MeldingAlias: aantal={len(urls)}, bron_urls={', '.join(urls)}"
