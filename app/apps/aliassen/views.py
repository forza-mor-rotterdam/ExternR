import logging

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger(__name__)


class MeldingNotificatieAPIView(APIView):
    def get(self, request):
        return Response({}, status=status.HTTP_200_OK)
