from apps.taken.admin_filters import (
    AfgeslotenOpFilter,
    ResolutieFilter,
    TaakstatusFilter,
    TitelFilter,
)
from apps.taken.models import Taak, Taakgebeurtenis, Taakstatus, Taaktype, TaakZoekData
from apps.taken.tasks import compare_and_update_status
from django.contrib import admin
from django.db.models import Count


class TaakAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "uuid",
        "titel",
        "taaktype",
        "melding",
        "taakstatus",
        "resolutie",
        "aangemaakt_op",
        "aangepast_op",
        "taakopdracht",
        "taak_zoek_data",
    )
    readonly_fields = (
        "uuid",
        "aangemaakt_op",
        "aangepast_op",
        "afgesloten_op",
    )
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "uuid",
                    "titel",
                    "melding",
                    "taaktype",
                    "taakstatus",
                    "resolutie",
                    "bericht",
                    "additionele_informatie",
                    "taakopdracht",
                    "taak_zoek_data",
                    "bezig_met_verwerken",
                )
            },
        ),
        (
            "Tijden",
            {
                "fields": (
                    "aangemaakt_op",
                    "aangepast_op",
                    "afgesloten_op",
                )
            },
        ),
    )
    search_fields = [
        "id",
        "uuid",
        "taakopdracht",
        "melding__bron_url",
    ]
    list_filter = (
        TaakstatusFilter,
        ResolutieFilter,
        AfgeslotenOpFilter,
        TitelFilter,
    )
    raw_id_fields = (
        "melding",
        "taaktype",
        "taakstatus",
        "taak_zoek_data",
    )
    actions = ["compare_taakopdracht_status"]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related(
            "melding",
            "taaktype",
            "taakstatus",
            "taak_zoek_data",
        )

    def compare_taakopdracht_status(self, request, queryset):
        voltooid_taak_ids = queryset.filter(taakstatus__naam="voltooid").values_list(
            "id", flat=True
        )
        for taak_id in voltooid_taak_ids:
            compare_and_update_status.delay(taak_id)
        self.message_user(
            request, f"Updating taakopdracht for {len(voltooid_taak_ids)} taken!"
        )

    compare_taakopdracht_status.short_description = (
        "Compare taak and taakopdracht status"
    )


class TaaktypeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "omschrijving",
        "aangemaakt_op",
    )


class TakenAantalFilter(admin.SimpleListFilter):
    title = "taken_aantal"
    parameter_name = "taak"

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
            queryset.annotate(taken_aantal=Count("taak"))
            .order_by()
            .filter(**{value: 0})
        )


class TaakZoekDataAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "aangemaakt_op",
        "display_geometrie",
        "melding_alias",
        "taken_aantal",
    )
    readonly_fields = ("display_geometrie",)
    raw_id_fields = ("melding_alias",)
    list_filter = (TakenAantalFilter,)
    search_fields = [
        "melding_alias__bron_url",
    ]

    def taken_aantal(self, obj):
        return str(obj.taak.count())

    def display_geometrie(self, obj):
        # Convert GEOSGeometry to JSON string representation
        return str(obj.geometrie.geojson) if obj.geometrie else None

    display_geometrie.short_description = "Geometrie (JSON)"  # Customize column header

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related(
            "melding_alias",
        ).prefetch_related(
            "taak",
        )


class TaakgebeurtenisAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "gebruiker",
    )


class TaakstatusAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "uuid",
        "naam",
        "taak",
        "aangemaakt_op",
        "aangepast_op",
    )


admin.site.register(TaakZoekData, TaakZoekDataAdmin)
admin.site.register(Taak, TaakAdmin)
admin.site.register(Taaktype, TaaktypeAdmin)
admin.site.register(Taakgebeurtenis, TaakgebeurtenisAdmin)
admin.site.register(Taakstatus, TaakstatusAdmin)
