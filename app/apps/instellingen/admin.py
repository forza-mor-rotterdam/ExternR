from apps.instellingen.models import Instelling
from django.contrib import admin


class InstellingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "mor_core_gebruiker_email",
        "mor_core_token_timeout",
        "taakr_basis_url",
        "onderwerpen_basis_url",
        "email_beheer",
    )


admin.site.register(Instelling, InstellingAdmin)
