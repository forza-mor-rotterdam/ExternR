from apps.authenticatie.models import Gebruiker, Profiel
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin


class GebruikerAdmin(UserAdmin):
    model = Gebruiker
    list_display = (
        "email",
        "is_staff",
        "is_active",
        "is_superuser",
    )
    list_filter = (
        "email",
        "is_staff",
        "is_active",
        "is_superuser",
    )
    fieldsets = (
        (None, {"fields": ("email", "password", "first_name", "last_name")}),
        ("MOR permissies", {"fields": ("groups",)}),
        ("Permissions", {"fields": ("is_staff", "is_active", "is_superuser")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "first_name",
                    "last_name",
                    "is_staff",
                    "is_active",
                    "is_superuser",
                ),
            },
        ),
    )
    search_fields = ("email",)
    ordering = ("email",)


class ProfielAdmin(admin.ModelAdmin):
    ...


admin.site.register(Gebruiker, GebruikerAdmin)
admin.site.register(Profiel, ProfielAdmin)
