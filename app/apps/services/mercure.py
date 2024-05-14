import json
import logging

import jwt
import requests
from django.conf import settings
from django.core.validators import URLValidator

logger = logging.getLogger(__name__)


class MercureService:
    _subscribe_targets = ["*"]
    _publish_targets = ["/taak/{id}/"]
    _mercure_url = None
    _mercure_publisher_jwt_key = None
    _mercure_subscriber_jwt_key = None

    class ConfigException(Exception):
        ...

    def __init__(self):
        try:
            validate = URLValidator()
            validate(settings.APP_MERCURE_PUBLIC_URL)
        except Exception as e:
            logentry = (
                f"Config error: APP_MERCURE_PUBLIC_URL is not a valid url, error: {e}"
            )
            logger.warning(logentry)
            raise MercureService.ConfigException(logentry)
        if not settings.MERCURE_PUBLISHER_JWT_KEY:
            logentry = "Config error: MERCURE_PUBLISHER_JWT_KEY is None"
            logger.warning(logentry)
            raise MercureService.ConfigException(logentry)
        if not settings.MERCURE_SUBSCRIBER_JWT_KEY:
            logentry = "Config error: MERCURE_SUBSCRIBER_JWT_KEY is None"
            logger.warning(logentry)
            raise MercureService.ConfigException(logentry)

        self._mercure_url = settings.APP_MERCURE_INTERNAL_URL
        self._mercure_publisher_jwt_key = settings.MERCURE_PUBLISHER_JWT_KEY
        self._mercure_subscriber_jwt_key = settings.MERCURE_SUBSCRIBER_JWT_KEY

    def _get_jwt_token(self, key):
        return jwt.encode(
            {
                "mercure": {
                    "subscribe": self._subscribe_targets,
                    "publish": self._publish_targets,
                }
            },
            key,
            algorithm="HS256",
        )

    def publish(self, topic: str, data: dict = {}):
        token = self._get_jwt_token(self._mercure_publisher_jwt_key)
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {
            "topic": topic,
            "data": json.dumps(data),
        }

        response = requests.post(
            self._mercure_url,
            data=data,
            headers=headers,
        )
        response.raise_for_status()

    def get_subscriber_token(self):
        return self._get_jwt_token(self._mercure_subscriber_jwt_key)
