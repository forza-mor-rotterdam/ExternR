import logging

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger(__name__)


class MeldingNotificatieAPIView(APIView):
    def get(self, request):
        # Has the potential of giving duplicate taak_zoek_data issues.
        # Taak zoek data is updated on changes to the melding or taak.
        # melding_alias, aangemaakt = MeldingAlias.objects.get_or_create(
        #     bron_url=request.GET.get("melding_url")
        # )
        # notificatie_type = request.GET.get("notificatie_type")
        # if notificatie_type != "taakopdracht_aangemaakt":
        #     task_update_melding_alias_data.delay(melding_alias.id)

        return Response({}, status=status.HTTP_200_OK)
