import logging

from apps.services.mercure import MercureService
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from utils.diversen import absolute

logger = logging.getLogger(__name__)


def general_settings(context):
    session_expiry_max_timestamp = context.session.get("_session_init_timestamp_", 0)
    if session_expiry_max_timestamp:
        session_expiry_max_timestamp += settings.SESSION_EXPIRE_MAXIMUM_SECONDS
    session_expiry_timestamp = context.session.get("_session_current_timestamp_", 0)
    if session_expiry_timestamp:
        session_expiry_timestamp += settings.SESSION_EXPIRE_SECONDS

    getattr(context, "user", None)

    mercure_service = None
    subscriber_token = None
    try:
        mercure_service = MercureService()
    except MercureService.ConfigException:
        ...

    if mercure_service:
        subscriber_token = mercure_service.get_subscriber_token()

    deploy_date_formatted = None
    if settings.DEPLOY_DATE:
        deploy_date = timezone.datetime.strptime(
            settings.DEPLOY_DATE, "%d-%m-%Y-%H-%M-%S"
        )
        deploy_date_formatted = deploy_date.strftime("%d-%m-%Y %H:%M:%S")

    return {
        "MELDINGEN_URL": settings.MELDINGEN_URL,
        "UI_SETTINGS": settings.UI_SETTINGS,
        "DEBUG": settings.DEBUG,
        "DEV_SOCKET_PORT": settings.DEV_SOCKET_PORT,
        "GET": context.GET,
        "ABSOLUTE_ROOT": absolute(context).get("ABSOLUTE_ROOT"),
        "SESSION_EXPIRY_MAX_TIMESTAMP": session_expiry_max_timestamp,
        "SESSION_EXPIRY_TIMESTAMP": session_expiry_timestamp,
        "SESSION_CHECK_INTERVAL_SECONDS": settings.SESSION_CHECK_INTERVAL_SECONDS,
        "LOGOUT_URL": reverse("oidc_logout"),
        "LOGIN_URL": f"{reverse('oidc_authentication_init')}?next={absolute(context).get('FULL_URL')}",
        "APP_MERCURE_PUBLIC_URL": settings.APP_MERCURE_PUBLIC_URL,
        "GIT_SHA": settings.GIT_SHA,
        "MERCURE_SUBSCRIBER_TOKEN": subscriber_token,
        "APP_ENV": settings.APP_ENV,
        "DEPLOY_DATE": deploy_date_formatted,
        "MOR_CORE_URL_PREFIX": settings.MOR_CORE_URL_PREFIX,
        "MOR_CORE_PROTECTED_URL_PREFIX": settings.MOR_CORE_PROTECTED_URL_PREFIX,
    }
