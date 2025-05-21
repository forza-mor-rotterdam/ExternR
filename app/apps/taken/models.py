from apps.aliassen.models import MeldingAlias
from apps.taken.managers import TaakManager
from apps.taken.querysets import TaakQuerySet
from django.contrib.gis.db import models
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from rest_framework.reverse import reverse as drf_reverse
from utils.models import BasisModel


class Taakgebeurtenis(BasisModel):
    """
    Taakgebeurtenissen bouwen de history op van een taak
    """

    class ResolutieOpties(models.TextChoices):
        OPGELOST = "opgelost", "Opgelost"
        NIET_OPGELOST = "niet_opgelost", "Niet opgelost"
        GEANNULEERD = "geannuleerd", "Geannuleerd"
        NIET_GEVONDEN = "niet_gevonden", "Niets aangetroffen"

    taakstatus = models.OneToOneField(
        to="taken.Taakstatus",
        related_name="taakgebeurtenis_voor_taakstatus",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    omschrijving_intern = models.CharField(max_length=5000, null=True, blank=True)
    gebruiker = models.CharField(max_length=200, null=True, blank=True)
    taak = models.ForeignKey(
        to="taken.Taak",
        related_name="taakgebeurtenissen_voor_taak",
        on_delete=models.CASCADE,
    )
    resolutie = models.CharField(
        max_length=50,
        choices=ResolutieOpties.choices,
        blank=True,
        null=True,
    )
    notificatie_verstuurd = models.BooleanField(default=True)

    class Meta:
        ordering = ("-aangemaakt_op",)
        verbose_name = "Taakgebeurtenis"
        verbose_name_plural = "Taakgebeurtenissen"


class Taaktype(BasisModel):
    omschrijving = models.CharField(max_length=200)
    toelichting = models.CharField(
        max_length=500,
        blank=True,
        null=True,
    )
    additionele_informatie = models.JSONField(default=dict)

    volgende_taaktypes = models.ManyToManyField(
        to="taken.Taaktype",
        related_name="vorige_taaktypes_voor_taaktype",
        blank=True,
    )
    actief = models.BooleanField(default=True)

    # ExternR specific fields
    externe_instantie = models.CharField(max_length=200, blank=False, null=False)
    externe_instantie_email = models.EmailField(unique=False, blank=False, null=False)
    externe_instantie_verantwoordelijke = models.CharField(
        max_length=200, blank=True, null=True
    )

    def taaktype_url(self, request):
        return drf_reverse(
            "v1:taaktype-detail",
            kwargs={"uuid": self.uuid},
            request=request,
        )

    class Meta:
        ordering = ("-aangemaakt_op",)
        verbose_name = "Taaktype"
        verbose_name_plural = "Taaktypes"

    def __str__(self) -> str:
        return f"{self.omschrijving}"


class Taakstatus(BasisModel):
    class NaamOpties(models.TextChoices):
        NIEUW = "nieuw", "Nieuw"
        TOEGEWEZEN = "toegewezen", "Toegewezen"
        OPENSTAAND = "openstaand", "Openstaand"
        VOLTOOID = "voltooid", "Voltooid"
        VOLTOOID_MET_FEEDBACK = "voltooid_met_feedback", "Voltooid met feedback"

    naam = models.CharField(
        max_length=50,
        choices=NaamOpties.choices,
        default=NaamOpties.NIEUW,
    )
    taak = models.ForeignKey(
        to="taken.Taak",
        related_name="taakstatussen_voor_taak",
        on_delete=models.CASCADE,
    )

    @classmethod
    def niet_voltooid_statussen(cls):
        return [
            choice[0]
            for choice in Taakstatus.NaamOpties.choices
            if choice[0]
            not in [
                Taakstatus.NaamOpties.VOLTOOID,
                Taakstatus.NaamOpties.VOLTOOID_MET_FEEDBACK,
            ]
        ]

    def volgende_statussen(self):
        naam_opties = [no[0] for no in Taakstatus.NaamOpties.choices]
        if self.naam not in naam_opties:
            return naam_opties

        if self.naam not in naam_opties:
            return naam_opties

        match self.naam:
            case Taakstatus.NaamOpties.NIEUW:
                return [
                    Taakstatus.NaamOpties.TOEGEWEZEN,
                    Taakstatus.NaamOpties.VOLTOOID,
                ]
            case Taakstatus.NaamOpties.TOEGEWEZEN:
                return [
                    Taakstatus.NaamOpties.OPENSTAAND,
                    Taakstatus.NaamOpties.VOLTOOID,
                ]
            case Taakstatus.NaamOpties.OPENSTAAND:
                return [
                    Taakstatus.NaamOpties.TOEGEWEZEN,
                    Taakstatus.NaamOpties.VOLTOOID,
                ]
            case Taakstatus.NaamOpties.VOLTOOID:
                return [
                    Taakstatus.NaamOpties.VOLTOOID_MET_FEEDBACK,
                ]
            case _:
                return []

    def clean(self):
        errors = {}
        huidige_status = self.taak.status.naam if self.taak.status else ""
        nieuwe_status = self.naam

        if nieuwe_status == huidige_status:
            error_msg = "Status verandering niet toegestaan: van `{from_state}` naar `{to_state}`.".format(
                from_state=huidige_status, to_state=nieuwe_status
            )
            errors["taakstatus"] = ValidationError(error_msg, code="invalid")

        if errors:
            raise ValidationError(errors)

    class TaakStatusVeranderingNietToegestaan(Exception):
        pass

    def __str__(self) -> str:
        return f"{self.naam}({self.pk})"

    class Meta:
        ordering = ("-aangemaakt_op",)
        verbose_name = "Taakstatus"
        verbose_name_plural = "Taakstatussen"


LOCATIE_TYPE_CHOICES = (
    ("adres", "adres"),
    ("lichtmast", "lichtmast"),
    ("graf", "graf"),
)


class TaakZoekData(BasisModel):
    locatie_type = models.CharField(
        max_length=50, choices=LOCATIE_TYPE_CHOICES, default=LOCATIE_TYPE_CHOICES[0][0]
    )
    # Locatie met hoogste gewicht
    plaatsnaam = models.CharField(max_length=255, null=True, blank=True)
    straatnaam = models.CharField(max_length=255, null=True, blank=True)
    huisnummer = models.IntegerField(null=True, blank=True)
    huisletter = models.CharField(max_length=1, null=True, blank=True)
    toevoeging = models.CharField(max_length=4, null=True, blank=True)
    postcode = models.CharField(max_length=7, null=True, blank=True)
    wijknaam = models.CharField(max_length=255, null=True, blank=True)
    buurtnaam = models.CharField(max_length=255, null=True, blank=True)
    # B&C Locatie info
    begraafplaats = models.CharField(max_length=50, null=True, blank=True)
    grafnummer = models.CharField(max_length=10, null=True, blank=True)
    vak = models.CharField(max_length=10, null=True, blank=True)
    # Lichtmast
    lichtmast_id = models.CharField(max_length=255, null=True, blank=True)
    # Geometrie
    geometrie = models.GeometryField(null=True, blank=True)
    # MeldR nummerers afkomstig uit signalen_voor_melding.bron_signaal_id
    bron_signaal_ids = ArrayField(
        models.CharField(max_length=500, blank=True), blank=True, null=True
    )

    melding_alias = models.ForeignKey(
        MeldingAlias,
        related_name="taak_zoek_data",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ("-aangemaakt_op",)
        verbose_name = "Taak zoek data"
        verbose_name_plural = "Taak zoek data"


class Taak(BasisModel):
    class ResolutieOpties(models.TextChoices):
        OPGELOST = "opgelost", "Opgelost"
        NIET_OPGELOST = "niet_opgelost", "Niet opgelost"
        GEANNULEERD = "geannuleerd", "Geannuleerd"
        NIET_GEVONDEN = "niet_gevonden", "Niets aangetroffen"

    afgesloten_op = models.DateTimeField(null=True, blank=True)
    verwijderd_op = models.DateTimeField(null=True, blank=True)
    melding = models.ForeignKey(
        to="aliassen.MeldingAlias",
        related_name="taken_voor_meldingalias",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    taakopdracht = models.URLField()
    taaktype = models.ForeignKey(
        to="taken.Taaktype",
        related_name="taken_voor_taaktype",
        on_delete=models.CASCADE,
    )
    taakstatus = models.OneToOneField(
        to="taken.Taakstatus",
        related_name="taak_voor_taakstatus",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    resolutie = models.CharField(
        max_length=50,
        choices=ResolutieOpties.choices,
        blank=True,
        null=True,
    )
    titel = models.CharField(max_length=200)
    bericht = models.CharField(
        max_length=5000,
        blank=True,
        null=True,
    )
    additionele_informatie = models.JSONField(default=dict)
    geometrie = models.GeometryField(null=True, blank=True)

    taak_zoek_data = models.ForeignKey(
        TaakZoekData,
        related_name="taak",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    bezig_met_verwerken = models.BooleanField(
        default=False,
    )

    objects = TaakQuerySet.as_manager()
    acties = TaakManager()

    def __str__(self) -> str:
        return f"{self.taaktype.omschrijving} - {self.titel}({self.pk})"

    def get_melding_alias(self):
        self.melding.save()
        return self.melding

    @classmethod
    def behandel_opties(cls):
        return (
            (
                Taak.ResolutieOpties.OPGELOST,
                "De taak is afgerond",
            ),
            (
                Taak.ResolutieOpties.NIET_OPGELOST,
                "Kan niet worden uitgevoerd",
            ),
        )

    def adres(self):
        if not self.taak_zoek_data:
            return ""
        if not self.taak_zoek_data.straatnaam:
            return ""
        if self.taak_zoek_data.straatnaam and not self.taak_zoek_data.huisnummer:
            return self.taak_zoek_data.straatnaam
        return f"{self.taak_zoek_data.straatnaam} {self.taak_zoek_data.huisnummer}{self.taak_zoek_data.huisletter if self.taak_zoek_data.huisletter else ''} {self.taak_zoek_data.toevoeging if self.taak_zoek_data.toevoeging else ''}".strip()

    class Meta:
        ordering = ("-aangemaakt_op",)
        verbose_name = "Taak"
        verbose_name_plural = "Taken"
