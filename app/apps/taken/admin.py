import ast
import importlib
import json

from apps.taken.admin_filters import (
    AfgeslotenOpFilter,
    ResolutieFilter,
    TaakstatusFilter,
    TitelFilter,
)
from apps.taken.models import Taak, Taakgebeurtenis, Taakstatus, Taaktype, TaakZoekData
from apps.taken.tasks import _send_taak_aangemaakt_email_task, compare_and_update_status
from django.contrib import admin, messages
from django.db.models import Count
from django.utils.safestring import mark_safe
from django_celery_results.admin import TaskResultAdmin
from django_celery_results.models import TaskResult


def retry_celery_task_admin_action(modeladmin, request, queryset):
    msg = ""
    for task_res in queryset:
        if task_res.status != "FAILURE":
            msg += f'{task_res.task_id} => Skipped. Not in "FAILURE" State<br>'
            continue
        try:
            task_actual_name = task_res.task_name.split(".")[-1]
            module_name = ".".join(task_res.task_name.split(".")[:-1])
            args = json.loads(task_res.task_args)
            kwargs = json.loads(task_res.task_kwargs)
            if isinstance(kwargs, str) and isinstance(args, str):
                kwargs = kwargs.replace("'", '"')
                args = ast.literal_eval(ast.literal_eval(task_res.task_args))
                kwargs = json.loads(kwargs)
                if kwargs or args:
                    getattr(
                        importlib.import_module(module_name), task_actual_name
                    ).apply_async(args=args, kwargs=kwargs, task_id=task_res.task_id)
            if not kwargs:
                args = ast.literal_eval(ast.literal_eval(task_res.task_args))
                getattr(
                    importlib.import_module(module_name), task_actual_name
                ).apply_async(args, task_id=task_res.task_id)
            msg += f"{task_res.task_id} => Successfully sent to queue for retry.<br>"
        except Exception as ex:
            msg += f"{task_res.task_id} => Unable to process. Error: {ex}<br>"
    messages.info(request, mark_safe(msg))


retry_celery_task_admin_action.short_description = "Retry Task"


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
    actions = ["compare_taakopdracht_status", "send_taak_aangemaakt_email"]

    def send_taak_aangemaakt_email(self, request, queryset):
        base_url = request.build_absolute_uri("/")[:-1]  # Remove trailing slash
        success_count = 0
        error_count = 0

        for taak in queryset:
            try:
                _send_taak_aangemaakt_email_task(taak.id, base_url=base_url)
                success_count += 1
            except Exception as e:
                error_count += 1
                self.message_user(
                    request,
                    f"Error sending email for Taak {taak.id}: {str(e)}",
                    level=messages.ERROR,
                )

        if success_count > 0:
            self.message_user(
                request,
                f"Successfully sent {success_count} email(s) for selected Taak(s).",
                level=messages.SUCCESS,
            )

        if error_count > 0:
            self.message_user(
                request,
                f"Failed to send {error_count} email(s). Check the error messages above.",
                level=messages.WARNING,
            )

    send_taak_aangemaakt_email.short_description = "Send Taak aangemaakt email"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related(
            "melding",
            "taaktype",
            "taakstatus",
            "taak_zoek_data",
        ).prefetch_related("taakgebeurtenissen_voor_taak")

    def compare_taakopdracht_status(self, request, queryset):
        voltooid_taak_ids = queryset.filter(
            taakstatus__naam__in=["voltooid", "voltooid_met_feedback"]
        ).values_list("id", flat=True)
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
        "taakstatus",
        "resolutie",
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


class CustomTaskResultAdmin(TaskResultAdmin):
    list_filter = (
        "status",
        "date_created",
        "date_done",
        "periodic_task_name",
        "task_name",
    )
    actions = [
        retry_celery_task_admin_action,
    ]


admin.site.unregister(TaskResult)
admin.site.register(TaskResult, CustomTaskResultAdmin)


admin.site.register(TaakZoekData, TaakZoekDataAdmin)
admin.site.register(Taak, TaakAdmin)
admin.site.register(Taaktype, TaaktypeAdmin)
admin.site.register(Taakgebeurtenis, TaakgebeurtenisAdmin)
admin.site.register(Taakstatus, TaakstatusAdmin)
