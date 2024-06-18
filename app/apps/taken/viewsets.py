from apps.aliassen.tasks import task_update_melding_alias_data
from apps.taken.models import Taak, Taaktype
from apps.taken.serializers import (
    TaakgebeurtenisStatusSerializer,
    TaakSerializer,
    TaaktypeSerializer,
)
from apps.taken.tasks import (
    send_taak_aangemaakt_email_task,
    taak_afsluiten_zonder_feedback_task,
)
from celery import chain
from drf_spectacular.utils import extend_schema
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response


class TaaktypeViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = "uuid"
    queryset = Taaktype.objects.all()

    serializer_class = TaaktypeSerializer

    permission_classes = ()

    @extend_schema(
        description="Taaktypes voor melding",
        responses={status.HTTP_200_OK: TaaktypeSerializer},
        parameters=None,
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="voor_melding",
        serializer_class=TaaktypeSerializer,
    )
    def voor_melding(self, request, melding_url):
        """
        minimale implementatie: geef alleen taaktypes terug voor deze melding, waar nog geen openstaande taken voor zijn.
        """
        taaktypes = (
            Taak.objects.select_related(
                "melding",
            )
            .filter(melding=melding_url)
            .values_list("taaktype", flat=True)
            .distinct()
        )
        serializer = TaaktypeSerializer(taaktypes)
        return Response(serializer.data)


class TaakViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    lookup_field = "uuid"
    queryset = Taak.objects.select_related(
        "melding",
        "taakstatus",
        "taak_zoek_data",
    ).all()

    serializer_class = TaakSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        taak = Taak.acties.aanmaken(serializer)

        base_url = request.build_absolute_uri("/")[:-1]  # Remove trailing slash

        chain_of_tasks = chain(
            task_update_melding_alias_data.si(taak.melding.id),
            send_taak_aangemaakt_email_task.si(taak.id, base_url=base_url),
        )

        if not taak.taaktype.externe_instantie_feedback_vereist:
            chain_of_tasks |= taak_afsluiten_zonder_feedback_task.si(taak.id)

        chain_of_tasks.delay()

        serializer = self.get_serializer(taak, context={"request": request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        description="Verander de status van een taak",
        request=TaakgebeurtenisStatusSerializer,
        responses={status.HTTP_200_OK: TaakSerializer},
        parameters=None,
    )
    @action(detail=True, methods=["patch"], url_path="status-aanpassen")
    def status_aanpassen(self, request, uuid):
        taak = self.get_object()
        data = {}
        data.update(request.data)
        data["taakstatus"]["taak"] = taak.id
        serializer = TaakgebeurtenisStatusSerializer(
            data=data,
            context={"request": request},
        )
        if serializer.is_valid():
            Taak.acties.status_aanpassen(serializer, self.get_object())

            serializer = TaakSerializer(self.get_object(), context={"request": request})
            return Response(serializer.data)
        return Response(
            data=serializer.errors,
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
