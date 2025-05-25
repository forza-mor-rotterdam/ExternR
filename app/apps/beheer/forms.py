from django import forms


class AchtegrondTasksAanmakenForm(forms.Form):
    taakgebeurtenis_ids = forms.CharField(widget=forms.HiddenInput())
