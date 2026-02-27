# ExternR – snelle onboarding (alleen automatisch mail versturen)

Deze applicatie heeft geen gebruikersinterface:
ExternR ontvangt gegevens uit de MOR-keten en verstuurt **op de achtergrond automatisch e-mails**.
Er is wel een beheerinterface voor instellingen voor gebruikers, taaktypen en e-mailadressen van externe partijen.

De twee belangrijkste onderdelen:
**(1) opmaak van de mail** en **(2) de verzend-pipeline**.

---

## 1) E-mail inhoud / layout (wat de ontvanger krijgt)
Zoek de Django e-mailtemplates.

Hier bepaal je:
- HTML structuur
- teksten
- welke velden uit de melding/taak worden gebruikt
- conditionele blokken (bijv. wel/geen contactinfo, bijlagen, categorieën)

➡️ Dit is de enige plek waar de daadwerkelijke communicatie naar buiten wordt gevormd.

Vuistregel:
> Wijzig gedrag altijd in Python, maar presentatie altijd in de template.

---

## 2) Verzendflow (wanneer er een mail uitgaat)
Zoek waar een taak of melding leidt tot een “send mail” actie.

De keten is typisch:

MOR event → Django verwerking → Celery taak → mail provider → status opgeslagen

Hier pas je aan:
- wanneer een mail wordt aangemaakt
- wie de ontvanger is
- retry gedrag
- foutafhandeling
- logging/audittrail

Belangrijk: verzending is async (Celery), dus HTTP-requests wachten niet op succes.

---

## Wat je waar aanpast

| Aanpassing | Bestandstype |
|----------|-----------|
| Tekst wijzigen | mail template |
| Velden toevoegen | context builder (Python) |
| Nieuwe ontvangerlogica | business logic / service |
| Niet meer versturen | trigger/condition |
| Opnieuw proberen bij fout | Celery task |

---

## Bekende issues
De applicatie is destijds ontwikkeld op een kopie van de FixeR-applicatie en bevat zodoende veel ongebruikte bestanden. Met name js-controllers. Een eerste verbetering zou het opschonen van ongebruikte bestanden kunnen zijn.
