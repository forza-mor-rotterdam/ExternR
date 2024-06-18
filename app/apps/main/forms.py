from apps.taken.models import Taak
from django import forms


class RadioSelect(forms.RadioSelect):
    option_template_name = "widgets/radio_option.html"


class RadioSelectSimple(forms.RadioSelect):
    option_template_name = "widgets/radio_option_simple.html"


class TaakBehandelForm(forms.Form):
    resolutie = forms.ChoiceField(
        widget=RadioSelectSimple(
            attrs={
                "class": "list--form-radio-input",
                "data-action": "change->incidentHandleForm#onChangeResolution",
                "hideLabel": True,
            }
        ),
        label="Is de taak afgehandeld?",
        choices=Taak.behandel_opties(),
        required=True,
    )

    bijlagen = forms.FileField(
        widget=forms.widgets.FileInput(
            attrs={
                "accept": ".jpg, .jpeg, .png, .heic",
                "data-action": "change->bijlagen#updateImageDisplay",
                "data-bijlagen-target": "bijlagenExtra",
                # "multiple": "multiple",
                "hideLabel": True,
            }
        ),
        label="Foto's",
        help_text="Help je collega’s en de melder door een volledig beeld van de situatie te geven.",
        required=False,
    )

    omschrijving_intern = forms.CharField(
        label="Interne opmerking",
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "data-testid": "information",
                "rows": "4",
                "data-meldingbehandelformulier-target": "internalText",
            }
        ),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        volgende_taaktypes = kwargs.pop("volgende_taaktypes", None)
        super().__init__(*args, **kwargs)

        # Vraag Vervolgtaak? Altijd tonen bij de 3 resoluties (afgehandeld, niet afgehandeld, niets aangetroffen)
        # Alle vervolgtaken als checkboxes weergeven?
        # Bij resolutie 3 ("kan  niet") is interne opmerking VERPLICHT, met tekst "Waarom kan de taak niet worden afgerond?"
        if volgende_taaktypes:
            self.fields["nieuwe_taak"] = forms.MultipleChoiceField(
                widget=forms.CheckboxSelectMultiple,
                label="",
                choices=[
                    (taaktype.id, taaktype.omschrijving)
                    for taaktype in volgende_taaktypes
                ],
                required=False,
            )
            # Omschrijving nieuwe taak nodig?
            self.fields["omschrijving_nieuwe_taak"] = forms.CharField(
                label="Toelichting",
                help_text="Deze tekst wordt niet naar de melder verstuurd.",
                widget=forms.Textarea(
                    attrs={
                        "class": "form-control",
                        "rows": "4",
                    }
                ),
                required=False,
            )


class SorteerFilterForm(forms.Form):
    sorteer_opties = forms.ChoiceField(
        widget=forms.Select(
            attrs={
                "data-action": "sorteerFilter#onChangeHandler",
                "data-sorteerFilter-target": "sorteerField",
            }
        ),
        choices=(
            ("Datum-reverse", "Datum (nieuwste bovenaan)"),
            ("Datum", "Datum (oudste bovenaan)"),
            ("Afstand", "Afstand"),
            ("Adres", "T.h.v. Adres (a-z)"),
            ("Adres-reverse", "T.h.v. Adres (z-a)"),
            ("Postcode", "Postcode (1000-9999)"),
            ("Postcode-reverse", "Postcode (9999-1000)"),
        ),
    )


class KaartModusForm(forms.Form):
    kaart_modus = forms.ChoiceField(
        widget=forms.RadioSelect(
            attrs={
                "class": "list--form-radio-input",
                "data-action": "click->kaartModus#kaartModusOptionClickHandler",
                "hideLabel": True,
            }
        ),
        choices=(
            ("volgen", "Volg mijn locatie"),
            ("toon_alles", "Toon alle taken"),
        ),
    )
