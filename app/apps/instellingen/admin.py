from apps.instellingen.models import Instelling
from django.contrib import admin


class InstellingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "mor_core_gebruiker_email",
        "mor_core_gebruiker_wachtwoord",
    )


admin.site.register(Instelling, InstellingAdmin)
