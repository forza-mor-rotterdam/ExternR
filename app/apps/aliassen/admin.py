from apps.aliassen.models import BijlageAlias, MeldingAlias
from apps.aliassen.tasks import task_update_melding_alias_data
from django.contrib import admin
from django.db.models import Count


@admin.action(description="Update melding alias data")
def action_update_melding_alias_data(self, request, queryset):
    for melding_alias in queryset:
        task_update_melding_alias_data.delay(melding_alias.id)


class TakenAantalFilter(admin.SimpleListFilter):
    title = "taken aantal"
    parameter_name = "taken_voor_meldingalias"

    def lookups(self, request, model_admin):
        return (
            ("taken_aantal__lte", "Geen taken"),
            ("taken_aantal__gt", "1 of meer taken"),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if not value:
            value = "taken_aantal__gte"
        return (
            queryset.annotate(taken_aantal=Count("taken_voor_meldingalias"))
            .order_by()
            .filter(**{value: 0})
        )


class ZoekDataAantalFilter(admin.SimpleListFilter):
    title = "zoek data aantal"
    parameter_name = "taak_zoek_data"

    def lookups(self, request, model_admin):
        return (
            ("zoek_data_aantal__lte", "Geen zoek data"),
            ("zoek_data_aantal__gt", "1 of meer zoek data"),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if not value:
            value = "zoek_data_aantal__gte"
        return (
            queryset.annotate(zoek_data_aantal=Count("taken_voor_meldingalias"))
            .order_by()
            .filter(**{value: 0})
        )


class ResponseDataFilter(admin.SimpleListFilter):
    title = "heeft response data"
    parameter_name = "response_json"

    def lookups(self, request, model_admin):
        return (
            ("has_not", "Geen response data"),
            ("has", "Wel response data"),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if not value:
            return queryset
        return queryset.filter(response_json__isnull=(value == "has_not"))


class MeldingAliasAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "bron_url",
        "aangepast_op",
        "taken_aantal",
        "taak_zoek_data_aantal",
        "heeft_response_data",
    )
    actions = (action_update_melding_alias_data,)
    search_fields = ("bron_url",)
    list_filter = (
        ResponseDataFilter,
        TakenAantalFilter,
        ZoekDataAantalFilter,
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related(
            "taak_zoek_data",
            "taken_voor_meldingalias",
        )

    def taken_aantal(self, obj):
        return str(obj.taken_voor_meldingalias.count())

    def taak_zoek_data_aantal(self, obj):
        return str(obj.taak_zoek_data.count())

    def heeft_response_data(self, obj):
        return bool(obj.response_json)


class BijlageAliasAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "bron_url",
    )


admin.site.register(MeldingAlias, MeldingAliasAdmin)
admin.site.register(BijlageAlias, BijlageAliasAdmin)
