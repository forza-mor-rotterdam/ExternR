from apps.meldingen.service import MeldingenService
from health_check.backends import BaseHealthCheckBackend
from health_check.exceptions import HealthCheckException


class MeldingenTokenCheck(BaseHealthCheckBackend):
    critical_service = False

    def check_status(self):
        try:
            MeldingenService().haal_token()
            return "OK"
        except Exception as e:
            raise HealthCheckException(e)

    def identifier(self):
        return self.__class__.__name__
