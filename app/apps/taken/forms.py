from apps.taken.models import Taaktype
from django import forms


class TaaktypeAanpassenForm(forms.ModelForm):
    omschrijving = forms.CharField(
        label="Titel",
        widget=forms.TextInput(
            attrs={
                "data-testid": "titel",
                "rows": "4",
            }
        ),
        required=True,
    )
    toelichting = forms.CharField(
        label="Omschrijving",
        widget=forms.Textarea(
            attrs={
                "data-testid": "omschrijving",
                "rows": "4",
            }
        ),
        required=False,
    )
    actief = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
        label="Actief",
        required=False,
    )
    redirect_field = forms.CharField(
        widget=forms.HiddenInput(),
        required=False,
    )

    class Meta:
        model = Taaktype
        fields = (
            "omschrijving",
            "toelichting",
            "actief",
            "externe_instantie",
            "externe_instantie_email",
            "externe_instantie_verantwoordelijke",
        )


class TaaktypeAanmakenForm(TaaktypeAanpassenForm):
    class Meta:
        model = Taaktype
        fields = (
            "omschrijving",
            "toelichting",
            "actief",
            "externe_instantie",
            "externe_instantie_email",
            "externe_instantie_verantwoordelijke",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields[
            "omschrijving"
        ].help_text = "Omschrijf het taaktype zo concreet mogelijk. Formuleer de gewenste actie, bijvoorbeeld ‘Grofvuil ophalen’."


class TaakFeedbackHandleForm(forms.Form):
    REDEN_CHOICES = (
        ("1", "De taak valt niet onder onze verantwoordelijkheid."),
        ("2", "We konden de locatie niet bereiken."),
        ("3", "Andere reden."),
    )
    omschrijving_intern_opties = forms.ChoiceField(
        label="Reden",
        widget=forms.RadioSelect(
            attrs={
                "data-action": "change->feedback#onChangeReden",
                "class": "list--form-radio-input",
            }
        ),
        choices=REDEN_CHOICES,
        required=True,
    )

    omschrijving_intern = forms.CharField(
        label="Toelichting",
        widget=forms.Textarea(
            attrs={
                "class": "hidden",
                "data-testid": "information",
                "rows": "4",
                "placeholder": "Omschrijf hier de reden",
            }
        ),
        required=True,
    )
