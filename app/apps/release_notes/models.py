import logging
import mimetypes
import os
from os.path import exists

from apps.authenticatie.forms import Gebruiker
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.db import models
from django.utils import timezone
from PIL import Image, UnidentifiedImageError
from pillow_heif import register_heif_opener
from sorl.thumbnail import get_thumbnail
from utils.images import get_upload_path
from utils.models import BasisModel

logger = logging.getLogger(__name__)


class Bijlage(BasisModel):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    bestand = models.FileField(
        upload_to=get_upload_path, null=False, blank=False, max_length=255
    )
    afbeelding = models.ImageField(
        upload_to=get_upload_path, null=True, blank=True, max_length=255
    )
    afbeelding_verkleind = models.ImageField(
        upload_to=get_upload_path, null=True, blank=True, max_length=255
    )

    mimetype = models.CharField(max_length=30, blank=False, null=False)
    is_afbeelding = models.BooleanField(default=False)

    class BestandPadFout(Exception):
        ...

    class AfbeeldingVersiesAanmakenFout(Exception):
        ...

    def _is_afbeelding(self):
        try:
            Image.open(self.bestand)
        except UnidentifiedImageError:
            return False
        return True

    def _heic_to_jpeg(self, file_field):
        register_heif_opener()

        with Image.open(file_field.path) as image:
            if image.mode != "RGB":
                image = image.convert("RGB")

            # Remove .heic extension and add .jpg
            new_file_name = f"{os.path.splitext(file_field.name)[0]}.jpg"

            image.save(os.path.join(settings.MEDIA_ROOT, new_file_name), "JPEG")

        return new_file_name

    def aanmaken_afbeelding_versies(self):
        mt = mimetypes.guess_type(self.bestand.path, strict=True)

        if exists(self.bestand.path):
            bestand = self.bestand.path
            self.is_afbeelding = self._is_afbeelding()
            if mt:
                self.mimetype = mt[0]
            if self.mimetype == "image/heic":
                bestand = self._heic_to_jpeg(self.bestand)
                self.is_afbeelding = True

            # Dont convert to jpeg if the image is a gif.
            if self.mimetype == "image/gif":
                return
            if self.is_afbeelding:
                try:
                    self.afbeelding_verkleind.name = get_thumbnail(
                        bestand,
                        settings.THUMBNAIL_KLEIN,
                        format="JPEG",
                        quality=99,
                    ).name
                    self.afbeelding.name = get_thumbnail(
                        bestand,
                        settings.THUMBNAIL_STANDAARD,
                        format="JPEG",
                        quality=80,
                    ).name
                except Exception as e:
                    raise Bijlage.AfbeeldingVersiesAanmakenFout(
                        f"aanmaken_afbeelding_versies: get_thumbnail fout: {e}"
                    )
        else:
            raise Bijlage.BestandPadFout(
                f"aanmaken_afbeelding_versies: bestand path bestaat niet, bijlage id: {self.pk}"
            )

    class Meta:
        verbose_name = "Bijlage"
        verbose_name_plural = "Bijlagen"


class ReleaseNote(BasisModel):
    titel = models.CharField(max_length=255)
    beschrijving = models.TextField(blank=True, max_length=1000)
    publicatie_datum = models.DateTimeField(null=False, blank=False)
    bijlagen = GenericRelation(Bijlage)
    versie = models.CharField(max_length=20, blank=True, null=True)
    bekeken_door_gebruikers = models.ManyToManyField(
        Gebruiker, blank=True, related_name="bekeken_release_notes"
    )

    def is_published(self):
        """
        Check if the release note is valid, i.e., not in the future and not older than five weeks.
        """
        five_weeks_ago = timezone.now() - timezone.timedelta(weeks=5)
        return not (
            self.publicatie_datum > timezone.now()
            or self.publicatie_datum < five_weeks_ago
        )

    def is_unwatched_by_user(self, user):
        """
        Check if the release note is unwatched by the user and meets the specified conditions.
        """
        return not self.bekeken_door_gebruikers.filter(pk=user.pk).exists()

    @staticmethod
    def count_unwatched(user):
        """
        Count the number of unwatched release notes for the user.
        """
        return sum(
            release_note.is_published() and release_note.is_unwatched_by_user(user)
            for release_note in ReleaseNote.objects.all()
        )

    def __str__(self):
        formatted_date = self.aangemaakt_op.strftime("%d-%m-%Y %H:%M:%S")
        return f"{self.titel} - {formatted_date}"
