import logging

from apps.aliassen.models import MeldingAlias
from apps.aliassen.tasks import task_update_melding_alias_data
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger(__name__)


class MeldingNotificatieAPIView(APIView):
    def get(self, request):
        melding_alias, aangemaakt = MeldingAlias.objects.get_or_create(
            bron_url=request.GET.get("melding_url")
        )
        notificatie_type = request.GET.get("notificatie_type")
        if notificatie_type != "taakopdracht_aangemaakt":
            task_update_melding_alias_data.delay(melding_alias.id)

        return Response({}, status=status.HTTP_200_OK)
