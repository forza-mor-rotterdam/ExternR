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

    @classmethod
    def actieve_instelling(cls):
        return cls.objects.first()
