import logging

from django.contrib.gis.db import models
from django.db import OperationalError, transaction
from django.dispatch import Signal
from django.utils import timezone

logger = logging.getLogger(__name__)

aangemaakt = Signal()
status_aangepast = Signal()
gebeurtenis_toegevoegd = Signal()


class TaakManager(models.Manager):
    class TaakInGebruik(Exception):
        ...

    def aanmaken(self, serializer, db="default"):
        from apps.aliassen.models import MeldingAlias
        from apps.taken.models import Taakgebeurtenis, Taakstatus, TaakZoekData

        with transaction.atomic():
            meldingalias, _ = MeldingAlias.objects.get_or_create(
                bron_url=serializer.validated_data.get("melding")
            )
            taak_zoek_data_instance, _ = TaakZoekData.objects.get_or_create(
                melding_alias=meldingalias,
            )

            serializer.validated_data["melding"] = meldingalias
            serializer.validated_data["taak_zoek_data"] = taak_zoek_data_instance
            gebruiker = serializer.validated_data.pop("gebruiker", None)
            taak = serializer.save()

            taakstatus = Taakstatus.objects.create(
                taak=taak,
            )
            Taakgebeurtenis.objects.create(
                taak=taak,
                taakstatus=taakstatus,
                gebruiker=gebruiker,
            )
            taak.taakstatus = taakstatus
            taak.save()

            transaction.on_commit(
                lambda: aangemaakt.send_robust(
                    sender=self.__class__,
                    taak=taak,
                )
            )
        return taak

    def status_aanpassen(self, serializer, taak, db="default"):
        from apps.aliassen.tasks import task_maak_bijlagealias
        from apps.taken.models import Taak

        with transaction.atomic():
            try:
                locked_taak = (
                    Taak.objects.using(db)
                    .select_for_update(nowait=True)
                    .get(pk=taak.pk)
                )
            except OperationalError:
                raise TaakManager.TaakInGebruik(
                    f"De taak is op dit moment in gebruik, probeer het later nog eens. taak nummer: {taak.id}, taak uuid: {taak.uuid}"
                )

            vorige_status = locked_taak.taakstatus
            resolutie = serializer.validated_data.pop("resolutie", None)
            bijlagen = serializer.validated_data.pop("bijlagen", None)
            uitvoerder = serializer.validated_data.pop("uitvoerder", None)
            taakgebeurtenis = serializer.save(
                taak=locked_taak,
            )
            for bijlage in bijlagen:
                task_maak_bijlagealias.delay(bijlage, taakgebeurtenis.pk)

            locked_taak.taakstatus = taakgebeurtenis.taakstatus
            locked_taak.additionele_informatie["uitvoerder"] = uitvoerder

            if not locked_taak.taakstatus.volgende_statussen():
                locked_taak.afgesloten_op = timezone.now().isoformat()
                if resolutie in [ro[0] for ro in Taak.ResolutieOpties.choices]:
                    locked_taak.resolutie = resolutie
            locked_taak.save()

            transaction.on_commit(
                lambda: status_aangepast.send_robust(
                    sender=self.__class__,
                    taak=locked_taak,
                    status=taakgebeurtenis.taakstatus,
                    vorige_status=vorige_status,
                )
            )

        return taak
