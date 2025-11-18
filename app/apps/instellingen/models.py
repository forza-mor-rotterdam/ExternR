from django.contrib.gis.db import models
from encrypted_model_fields.fields import EncryptedCharField
from utils.models import BasisModel


class Instelling(BasisModel):
    mor_core_basis_url = models.URLField(default="http://core.mor.local:8002")
    mor_core_gebruiker_email = models.EmailField()
    mor_core_gebruiker_wachtwoord = EncryptedCharField(max_length=100)
    mor_core_token_timeout = models.PositiveIntegerField(default=0)
    taakr_basis_url = models.URLField(default="http://taakr.mor.local:8009")
    onderwerpen_basis_url = models.URLField(default="http://onderwerpen.mor.local:8006")
    locaties_basis_url = models.URLField(default="http://locaties.mor.local:8010")
    email_beheer = models.EmailField()

    @classmethod
    def actieve_instelling(cls):
        actieve_instellingen = cls.objects.all()
        if not actieve_instellingen:
            raise Exception("Er zijn nog geen instellingen aangemaakt")
        return actieve_instellingen[0]

    def valideer_url(self, veld, url):
        if veld not in (
            "mor_core_basis_url",
            "taakr_basis_url",
            "onderwerpen_basis_url",
            "locaties_basis_url",
        ):
            return False
        return url.startswith(getattr(self, veld))
