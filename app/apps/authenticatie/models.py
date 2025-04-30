from apps.authenticatie.managers import GebruikerManager
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.contrib.gis.db import models
from django.forms.models import model_to_dict
from django.utils.html import mark_safe
from utils.fields import DictJSONField
from utils.models import BasisModel


class Gebruiker(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    telefoonnummer = models.CharField(max_length=17, blank=True, null=True)
    verwijderd_op = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = GebruikerManager()

    def __str__(self):
        if self.first_name:
            return f"{self.first_name}{' ' if self.last_name else ''}{self.last_name}"
        return self.email

    @property
    def rechtengroep(self):
        return mark_safe(
            f"{self.groups.all().first().name if self.groups.all() else ''}"
        )

    @property
    def rol(self):
        return mark_safe(f"{self.profiel.context.naam if self.profiel.context else ''}")

    def serialized_instance(self):
        if not self.is_authenticated:
            return None
        dict_instance = model_to_dict(
            self, fields=["email", "first_name", "last_name", "telefoonnummer"]
        )
        dict_instance.update(
            {
                "naam": self.__str__(),
                "rol": self.profiel.context.naam
                if hasattr(self, "profiel")
                and hasattr(self.profiel, "context")
                and hasattr(self.profiel.context, "naam")
                else None,
                "rechten": (
                    self.groups.all().first().name if self.groups.all() else None
                ),
            }
        )

        return dict_instance


User = get_user_model()


class Profiel(BasisModel):
    """
    Profiel model voor Gebruikers
    """

    gebruiker = models.OneToOneField(
        to=User,
        related_name="profiel",
        on_delete=models.CASCADE,
    )

    filters = DictJSONField(default=dict)
    ui_instellingen = DictJSONField(default=dict)
    context = models.ForeignKey(
        to="context.Context",
        related_name="profielen_voor_context",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    def __str__(self):
        if self.gebruiker:
            return f"Profiel voor: {self.gebruiker}"
        return f"Profiel id: {self.pk}"
