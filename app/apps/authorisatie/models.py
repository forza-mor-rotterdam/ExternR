from django.contrib.gis.db import models


class BasisPermissie:
    naam = None
    codenaam = None


class TaakBekijkenPermissie(BasisPermissie):
    naam = "Taak bekijken"
    codenaam = "taak_bekijken"


class TakenLijstBekijkenPermissie(BasisPermissie):
    naam = "Taken lijst bekijken"
    codenaam = "taken_lijst_bekijken"


class TaakAanmakenPermissie(BasisPermissie):
    naam = "Taak aanmaken"
    codenaam = "taak_aanmaken"


class TaakAfrondenPermissie(BasisPermissie):
    naam = "Taak afronden"
    codenaam = "taak_afronden"


class GebruikerLijstBekijkenPermissie(BasisPermissie):
    naam = "Gebruiker lijst bekijken"
    codenaam = "gebruiker_lijst_bekijken"


class GebruikerAanmakenPermissie(BasisPermissie):
    naam = "Gebruiker aanmaken"
    codenaam = "gebruiker_aanmaken"


class GebruikerBekijkenPermissie(BasisPermissie):
    naam = "Gebruiker bekijken"
    codenaam = "gebruiker_bekijken"


class GebruikerAanpassenPermissie(BasisPermissie):
    naam = "Gebruiker aanpassen"
    codenaam = "gebruiker_aanpassen"


class GebruikerVerwijderenPermissie(BasisPermissie):
    naam = "Gebruiker verwijderen"
    codenaam = "gebruiker_verwijderen"


class BeheerBekijkenPermissie(BasisPermissie):
    naam = "Beheer bekijken"
    codenaam = "beheer_bekijken"


class TaaktypeLijstBekijkenPermissie(BasisPermissie):
    naam = "Taaktype lijst bekijken"
    codenaam = "taaktype_lijst_bekijken"


class TaaktypeAanmakenPermissie(BasisPermissie):
    naam = "Taaktype aanmaken"
    codenaam = "taaktype_aanmaken"


class TaaktypeBekijkenPermissie(BasisPermissie):
    naam = "Taaktype bekijken"
    codenaam = "taaktype_bekijken"


class TaaktypeAanpassenPermissie(BasisPermissie):
    naam = "Taaktype aanpassen"
    codenaam = "taaktype_aanpassen"


class AfzenderEmailadresLijstBekijkenPermissie(BasisPermissie):
    naam = "Afzender emailadres lijst bekijken"
    codenaam = "afzender_emailadres_lijst_bekijken"


class AfzenderEmailadresAanmakenPermissie(BasisPermissie):
    naam = "Afzender emailadres aanmaken"
    codenaam = "afzender_emailadres_aanmaken"


class AfzenderEmailadresAanpassenPermissie(BasisPermissie):
    naam = "Afzender emailadres aanpassen"
    codenaam = "afzender_emailadres_aanpassen"


class AfzenderEmailadresVerwijderenPermissie(BasisPermissie):
    naam = "Afzender emailadres verwijderen"
    codenaam = "afzender_emailadres_verwijderen"


class ContextLijstBekijkenPermissie(BasisPermissie):
    naam = "Rol lijst bekijken"
    codenaam = "context_lijst_bekijken"


class ContextAanmakenPermissie(BasisPermissie):
    naam = "Rol aanmaken"
    codenaam = "context_aanmaken"


class ContextBekijkenPermissie(BasisPermissie):
    naam = "Rol bekijken"
    codenaam = "context_bekijken"


class ContextAanpassenPermissie(BasisPermissie):
    naam = "Rol aanpassen"
    codenaam = "context_aanpassen"


class ContextVerwijderenPermissie(BasisPermissie):
    naam = "Context verwijderen"
    codenaam = "context_verwijderen"


class RechtengroepLijstBekijkenPermissie(BasisPermissie):
    naam = "Rechtengroep lijst bekijken"
    codenaam = "rechtengroep_lijst_bekijken"


class RechtengroepAanmakenPermissie(BasisPermissie):
    naam = "Rechtengroep aanmaken"
    codenaam = "rechtengroep_aanmaken"


class RechtengroepBekijkenPermissie(BasisPermissie):
    naam = "Rechtengroep bekijken"
    codenaam = "rechtengroep_bekijken"


class RechtengroepAanpassenPermissie(BasisPermissie):
    naam = "Rechtengroep aanpassen"
    codenaam = "rechtengroep_aanpassen"


class RechtengroepVerwijderenPermissie(BasisPermissie):
    naam = "Rechtengroep verwijderen"
    codenaam = "rechtengroep_verwijderen"


# Melder info bekijken
class MelderGegevensBekijkenPermissie(BasisPermissie):
    naam = "Melder gegevens bekijken"
    codenaam = "melder_gegevens_bekijken"


gebruikersgroep_permissies = (
    TakenLijstBekijkenPermissie,
    TaakBekijkenPermissie,
    TaakAanmakenPermissie,
    TaakAfrondenPermissie,
    GebruikerLijstBekijkenPermissie,
    GebruikerAanmakenPermissie,
    GebruikerAanpassenPermissie,
    GebruikerBekijkenPermissie,
    GebruikerVerwijderenPermissie,
    BeheerBekijkenPermissie,
    TaaktypeLijstBekijkenPermissie,
    TaaktypeAanmakenPermissie,
    TaaktypeBekijkenPermissie,
    TaaktypeAanpassenPermissie,
    AfzenderEmailadresLijstBekijkenPermissie,
    AfzenderEmailadresAanmakenPermissie,
    AfzenderEmailadresAanpassenPermissie,
    AfzenderEmailadresVerwijderenPermissie,
    ContextLijstBekijkenPermissie,
    ContextAanmakenPermissie,
    ContextBekijkenPermissie,
    ContextAanpassenPermissie,
    ContextVerwijderenPermissie,
    RechtengroepLijstBekijkenPermissie,
    RechtengroepAanmakenPermissie,
    RechtengroepBekijkenPermissie,
    RechtengroepAanpassenPermissie,
    RechtengroepVerwijderenPermissie,
    MelderGegevensBekijkenPermissie,
)

gebruikersgroep_permissie_opties = [
    (p.codenaam, p.naam) for p in gebruikersgroep_permissies
]
permissie_namen = {p.codenaam: p.naam for p in gebruikersgroep_permissies}


class Permissie(models.Model):
    class Meta:
        managed = False
        default_permissions = ()
        permissions = gebruikersgroep_permissie_opties
