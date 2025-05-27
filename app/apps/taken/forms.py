from apps.taken.models import AfzenderEmailadres, Taaktype
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
            # "afzender_email",
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
            # "afzender_email",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields[
            "omschrijving"
        ].help_text = "Omschrijf het taaktype zo concreet mogelijk. Formuleer de gewenste actie, bijvoorbeeld ‘Grofvuil ophalen’."


class TaakFeedbackHandleForm(forms.Form):
    omschrijving_intern = forms.CharField(
        label="Toelichting",
        widget=forms.Textarea(
            attrs={
                "data-testid": "information",
                "rows": "4",
                "placeholder": "Toelichting",
            }
        ),
        required=False,
    )


class AfzenderEmailadresForm(forms.ModelForm):
    wijken = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple())

    def __init__(self, *args, **kwargs):
        wijk_opties = kwargs.pop("wijk_opties", [])
        super().__init__(*args, **kwargs)
        self.fields["wijken"].choices = wijk_opties

    class Meta:
        model = AfzenderEmailadres
        fields = (
            "email",
            "wijken",
        )
