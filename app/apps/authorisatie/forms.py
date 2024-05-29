from apps.authorisatie.models import permissie_namen
from django import forms
from django.contrib.auth.models import Group, Permission


class RechtengroepAanpassenForm(forms.ModelForm):
    name = forms.CharField(
        label="Naam",
        required=True,
    )
    permissions = forms.ModelMultipleChoiceField(
        widget=forms.CheckboxSelectMultiple(
            attrs={
                "class": "form-check-input",
            }
        ),
        queryset=Permission.objects.filter(content_type__app_label="authorisatie"),
        label="Rechten",
        required=False,
    )

    class Meta:
        model = Group
        fields = (
            "name",
            "permissions",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["permissions"].choices = [
            (
                permission.pk,
                permissie_namen.get(permission.codename, permission.codename),
            )
            for permission in Permission.objects.filter(
                content_type__app_label="authorisatie"
            )
        ]


class RechtengroepAanmakenForm(RechtengroepAanpassenForm):
    class Meta:
        model = Group
        fields = (
            "name",
            "permissions",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields[
            "permissions"
        ].help_text = (
            "Selecteer de rechten die onderdeel zullen zijn van de rechtengroep."
        )
