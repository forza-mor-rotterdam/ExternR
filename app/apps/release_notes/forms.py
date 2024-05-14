import logging

from ckeditor.widgets import CKEditorWidget
from django import forms
from django.contrib.contenttypes.forms import generic_inlineformset_factory

from .models import Bijlage, ReleaseNote

logger = logging.getLogger(__name__)

BijlageFormSet = generic_inlineformset_factory(
    Bijlage,
    fields=["bestand"],
    extra=0,
    can_delete=True,
)


class ReleaseNoteAanpassenForm(forms.ModelForm):
    titel = forms.CharField(
        label="Titel",
        widget=forms.TextInput(),
    )
    beschrijving = forms.CharField(
        widget=CKEditorWidget(
            attrs={
                "name": "beschrijving",
            }
        ),
        label="Beschrijving",
        max_length=1000,
    )

    # Currently not used
    # versie = forms.CharField(label="Versie", widget=forms.TextInput(), required=False)

    publicatie_datum = forms.DateTimeField(
        label="Publicatie datum",
        required=True,
        help_text="Release notes worden vanaf de publicatie datum 5 weken lang getoond.",
    )

    bijlagen = forms.FileField(
        label="Afbeelding of GIF",
        required=False,
        widget=forms.widgets.FileInput(
            attrs={
                "accept": ".jpg, .jpeg, .png, .heic, .gif",
                "data-action": "change->bijlagen#updateImageDisplay",
                "data-bijlagen-target": "bijlagenExtra",
                "multiple": "multiple",
                "hideLabel": True,
            }
        ),
    )

    formset = BijlageFormSet(queryset=Bijlage.objects.none(), prefix="bijlage")

    class Meta:
        model = ReleaseNote
        fields = [
            "titel",
            "beschrijving",
            # "versie",
            "publicatie_datum",
        ]


class ReleaseNoteAanmakenForm(ReleaseNoteAanpassenForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.fields[
        #     "titel"
        # ].help_text = "Geef een titel op voor de standaard tekst."
        # self.fields[
        #     "tekst"
        # ].help_text = "Geef een standaard tekst op van maximaal 2000 tekens. Deze tekst kan bij het afhandelen van een melding aangepast worden."


class ReleaseNoteSearchForm(forms.Form):
    search = forms.CharField(
        label="Zoeken",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Zoek release note"}),
    )
