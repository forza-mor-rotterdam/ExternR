from apps.taken.models import Taaktype
from django import forms


class TaaktypeAanpassenForm(forms.ModelForm):
    def __init__(self, *args, current_taaktype=None, **kwargs):
        super().__init__(*args, **kwargs)
        if current_taaktype:
            self.fields["volgende_taaktypes"].queryset = Taaktype.objects.filter(
                actief=True
            ).exclude(id=current_taaktype.id)

    volgende_taaktypes = forms.ModelMultipleChoiceField(
        widget=forms.CheckboxSelectMultiple(attrs={"class": "form-check-input"}),
        queryset=Taaktype.objects.filter(actief=True),
        label="Volgende taaktypes",
        required=False,
    )
    actief = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
        label="Actief",
        required=False,
    )

    class Meta:
        model = Taaktype
        fields = (
            "omschrijving",
            "externe_instantie_naam",
            "externe_instantie_email",
            "externe_instantie_feedback_vereist",
            "externe_instantie_naam_verantwoordelijke",
            "volgende_taaktypes",
            "actief",
        )


class TaaktypeAanmakenForm(TaaktypeAanpassenForm):
    class Meta:
        model = Taaktype
        fields = (
            "omschrijving",
            "externe_instantie_naam",
            "externe_instantie_email",
            "externe_instantie_feedback_vereist",
            "externe_instantie_naam_verantwoordelijke",
            "volgende_taaktypes",
            "actief",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields[
            "omschrijving"
        ].help_text = "Omschrijf het taaktype zo concreet mogelijk. Formuleer de gewenste actie, bijvoorbeeld ‘Grofvuil ophalen’."
        self.fields[
            "volgende_taaktypes"
        ].help_text = "Dit zijn taken die mogelijk uitgevoerd moeten worden nadat de taak is afgerond."


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
