from apps.context.models import Context
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

Gebruiker = get_user_model()


class GebruikerAanpassenForm(forms.ModelForm):
    context = forms.ModelChoiceField(
        queryset=Context.objects.all(),
        label="Rol",
        required=True,
    )
    group = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        label="Rechtengroep",
        required=False,
    )

    class Meta:
        model = Gebruiker
        fields = ("telefoonnummer", "first_name", "last_name", "group", "context")


class GebruikerAanmakenForm(GebruikerAanpassenForm):
    class Meta:
        model = Gebruiker
        fields = (
            "email",
            "telefoonnummer",
            "first_name",
            "last_name",
            "group",
            "context",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields[
            "email"
        ].help_text = "Gebruik altijd het e-mailadres van de gemeente."
        self.fields[
            "context"
        ].help_text = (
            "Bestaat de juiste rol voor deze gebruiker niet, maak deze eerst aan."
        )
        self.fields[
            "group"
        ].help_text = "Bestaat de juiste rechtengroep voor deze gebruiker niet, maak deze eerst aan."


class GebruikerProfielForm(forms.ModelForm):
    telefoonnummer = forms.CharField(
        label="Telefoonnummer",
        required=False,
        widget=forms.TextInput(attrs={"readonly": "readonly"}),
    )

    first_name = forms.CharField(
        label="Voornaam",
        required=False,
        widget=forms.TextInput(attrs={"readonly": "readonly"}),
    )

    last_name = forms.CharField(
        label="Achternaam",
        required=False,
        widget=forms.TextInput(attrs={"readonly": "readonly"}),
    )

    class Meta:
        model = Gebruiker
        fields = ("telefoonnummer", "first_name", "last_name")
