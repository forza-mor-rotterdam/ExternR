from django.contrib.gis.db import models


class BasisPermissie:
    naam = None
    codenaam = None


class GebruikerLijstBekijkenPermissie(BasisPermissie):
    naam = "Gebruiker lijst bekijken"
    codenaam = "gebruiker_lijst_bekijken"


class GebruikerAanmakenPermissie(BasisPermissie):
    naam = "Gebruiker aanmaken"
    codenaam = "gebruiker_aanmaken"


class GebruikerAanpassenPermissie(BasisPermissie):
    naam = "Gebruiker aanpassen"
    codenaam = "gebruiker_aanpassen"


class GebruikerVerwijderenPermissie(BasisPermissie):
    naam = "Gebruiker verwijderen"
    codenaam = "gebruiker_verwijderen"


class GebruikerTerughalenPermissie(BasisPermissie):
    naam = "Gebruiker terughalen"
    codenaam = "gebruiker_terughalen"


class BeheerBekijkenPermissie(BasisPermissie):
    naam = "Beheer bekijken"
    codenaam = "beheer_bekijken"


class TaaktypeLijstBekijkenPermissie(BasisPermissie):
    naam = "Taaktype lijst bekijken"
    codenaam = "taaktype_lijst_bekijken"


class TaaktypeAanmakenPermissie(BasisPermissie):
    naam = "Taaktype aanmaken"
    codenaam = "taaktype_aanmaken"


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


class RechtengroepLijstBekijkenPermissie(BasisPermissie):
    naam = "Rechtengroep lijst bekijken"
    codenaam = "rechtengroep_lijst_bekijken"


class RechtengroepAanmakenPermissie(BasisPermissie):
    naam = "Rechtengroep aanmaken"
    codenaam = "rechtengroep_aanmaken"


class RechtengroepAanpassenPermissie(BasisPermissie):
    naam = "Rechtengroep aanpassen"
    codenaam = "rechtengroep_aanpassen"


class RechtengroepVerwijderenPermissie(BasisPermissie):
    naam = "Rechtengroep verwijderen"
    codenaam = "rechtengroep_verwijderen"


gebruikersgroep_permissies = (
    GebruikerLijstBekijkenPermissie,
    GebruikerAanmakenPermissie,
    GebruikerAanpassenPermissie,
    GebruikerVerwijderenPermissie,
    GebruikerTerughalenPermissie,
    BeheerBekijkenPermissie,
    TaaktypeLijstBekijkenPermissie,
    TaaktypeAanmakenPermissie,
    TaaktypeAanpassenPermissie,
    AfzenderEmailadresLijstBekijkenPermissie,
    AfzenderEmailadresAanmakenPermissie,
    AfzenderEmailadresAanpassenPermissie,
    AfzenderEmailadresVerwijderenPermissie,
    RechtengroepLijstBekijkenPermissie,
    RechtengroepAanmakenPermissie,
    RechtengroepAanpassenPermissie,
    RechtengroepVerwijderenPermissie,
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
