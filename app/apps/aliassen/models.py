import json
import logging

from apps.meldingen.service import MeldingenService
from django.contrib.gis.db import models
from django.contrib.gis.geos import GEOSGeometry
from utils.models import BasisModel

logger = logging.getLogger(__name__)


class MeldingAlias(BasisModel):
    bron_url = models.CharField(max_length=500, unique=True)
    response_json = models.JSONField(
        default=dict,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Melding alias"
        verbose_name_plural = "Melding aliassen"

    class MeldingNietValide(Exception):
        pass

    def valideer_bron_url(self):
        response = MeldingenService().get_by_uri(self.bron_url)
        if response.status_code != 200:
            self.response_json = {}
            logger.error(
                f"Melding ophalen fout: status code: {response.status_code}, melding_alias id: {self.id}"
            )
            return
        self.response_json = response.json()

    def update_zoek_data(self):
        from apps.taken.models import TaakZoekData

        location_data = self.response_json.get("locaties_voor_melding")[0]
        signalen = self.response_json.get("signalen_voor_melding", [])
        signaal_ids = [signaal.get("bron_signaal_id") for signaal in signalen]

        # Retrieve or create TaakZoekData instance based on the unique identifier
        taak_zoek_data_instance, _ = TaakZoekData.objects.update_or_create(
            melding_alias=self,
            defaults={
                "geometrie": GEOSGeometry(json.dumps(location_data.get("geometrie")))
                if location_data.get("geometrie")
                else None,
                "locatie_type": location_data.get("locatie_type"),
                "plaatsnaam": location_data.get("plaatsnaam"),
                "straatnaam": location_data.get("straatnaam"),
                "huisnummer": location_data.get("huisnummer"),
                "huisletter": location_data.get("huisletter"),
                "toevoeging": location_data.get("toevoeging"),
                "postcode": location_data.get("postcode"),
                "wijknaam": location_data.get("wijknaam"),
                "buurtnaam": location_data.get("buurtnaam"),
                "begraafplaats": location_data.get("begraafplaats"),
                "grafnummer": location_data.get("grafnummer"),
                "vak": location_data.get("vak"),
                "lichtmast_id": location_data.get("lichtmast_id"),
                "bron_signaal_ids": signaal_ids,
            },
        )
        # Associate the retrieved TaakZoekData instance with all Taak instances associated with the melding_alias only if the instance is not already set on de taak
        for taak in self.taken_voor_meldingalias.filter(taak_zoek_data__isnull=True):
            taak.taak_zoek_data = taak_zoek_data_instance
            taak.save()

    def __str__(self) -> str:
        try:
            return self.response_json.get("name", self.bron_url)
        except Exception:
            return self.bron_url


class BijlageAlias(BasisModel):
    bron_url = models.CharField(max_length=500)
    response_json = models.JSONField(
        default=dict,
        blank=True,
        null=True,
    )
    taak_gebeurtenis = models.ForeignKey(
        to="taken.Taakgebeurtenis",
        related_name="bijlagen_voor_taak_gebeurtenis",
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = "Bijlage alias"
        verbose_name_plural = "Bijlage aliassen"

    class BijlageNietValide(Exception):
        pass

    def valideer_bron_url(self):
        response = MeldingenService().get_by_uri(self.bron_url)
        if response.status_code != 200:
            raise BijlageAlias.BijlageNietValide(
                f"Response status_code: {response.status_code}"
            )
        self.response_json = response.json()

    def __str__(self) -> str:
        return self.bron_url
