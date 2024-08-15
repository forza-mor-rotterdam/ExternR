from apps.taken.models import Taak, Taakgebeurtenis
from django.contrib import admin
from django.db.models import F, OuterRef, Subquery
from django.utils.translation import gettext_lazy as _


class TaakstatusFilter(admin.SimpleListFilter):
    title = _("Taakstatus")
    parameter_name = "taakstatus"

    def lookups(self, request, model_admin):
        status_namen = Taak.objects.values_list(
            "taakstatus__naam", flat=True
        ).distinct()
        return ((status_naam, status_naam) for status_naam in set(status_namen))

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(taakstatus__naam=self.value())
        return queryset


class ResolutieFilter(admin.SimpleListFilter):
    title = _("Resolutie")
    parameter_name = "resolutie"

    def lookups(self, request, model_admin):
        return Taak.ResolutieOpties.choices

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(resolutie=self.value())
        else:
            return queryset


class TitelFilter(admin.SimpleListFilter):
    title = _("Titel")
    parameter_name = "titel"

    def lookups(self, request, model_admin):
        titles = Taak.objects.values_list("titel", flat=True).distinct()
        return ((title, title) for title in sorted(set(titles)))

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(titel=self.value())
        return queryset


class AfgeslotenOpFilter(admin.SimpleListFilter):
    title = _("Afgesloten")
    parameter_name = "afgesloten"

    def lookups(self, request, model_admin):
        return (
            ("ja", _("Ja")),
            ("nee", _("Nee")),
        )

    def queryset(self, request, queryset):
        if self.value() == "ja":
            return queryset.exclude(afgesloten_op__isnull=True)
        elif self.value() == "nee":
            return queryset.filter(afgesloten_op__isnull=True)
        else:
            return queryset
