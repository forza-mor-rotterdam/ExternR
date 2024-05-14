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


class TaakToewijzenPermissie(BasisPermissie):
    naam = "Taak toewijzen"
    codenaam = "taak_toewijzen"


class TaakToewijzingIntrekkenPermissie(BasisPermissie):
    naam = "Taak toewijzing intrekken"
    codenaam = "taak_toewijzing_intrekken"


class TaakDelenPermissie(BasisPermissie):
    naam = "Taak delen"
    codenaam = "taak_delen"


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


# Release notes
class ReleaseNoteLijstBekijkenPermissie(BasisPermissie):
    naam = "Release notes bekijken"
    codenaam = "release_note_lijst_bekijken"


class ReleaseNoteAanmakenPermissie(BasisPermissie):
    naam = "Release note aanmaken"
    codenaam = "release_note_aanmaken"


class ReleaseNoteBekijkenPermissie(BasisPermissie):
    naam = "Release note bekijken"
    codenaam = "release_note_bekijken"


class ReleaseNoteAanpassenPermissie(BasisPermissie):
    naam = "Release note aanpassen"
    codenaam = "release_note_aanpassen"


class ReleaseNoteVerwijderenPermissie(BasisPermissie):
    naam = "Release note verwijderen"
    codenaam = "release_note_verwijderen"


# Homepage
class HomePageBekijkenPermissie(BasisPermissie):
    naam = "Homepage bekijken"
    codenaam = "homepage_bekijken"


# Melder info bekijken
class MelderGegevensBekijkenPermissie(BasisPermissie):
    naam = "Melder gegevens bekijken"
    codenaam = "melder_gegevens_bekijken"


gebruikersgroep_permissies = (
    TakenLijstBekijkenPermissie,
    TaakBekijkenPermissie,
    TaakAanmakenPermissie,
    TaakAfrondenPermissie,
    TaakToewijzenPermissie,
    TaakToewijzingIntrekkenPermissie,
    TaakDelenPermissie,
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
    ReleaseNoteLijstBekijkenPermissie,
    ReleaseNoteAanmakenPermissie,
    ReleaseNoteBekijkenPermissie,
    ReleaseNoteAanpassenPermissie,
    ReleaseNoteVerwijderenPermissie,
    HomePageBekijkenPermissie,
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
