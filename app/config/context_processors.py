import logging

from apps.instellingen.models import Instelling
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

    deploy_date_formatted = None
    if settings.DEPLOY_DATE:
        deploy_date = timezone.datetime.strptime(
            settings.DEPLOY_DATE, "%d-%m-%Y-%H-%M-%S"
        )
        deploy_date_formatted = deploy_date.strftime("%d-%m-%Y %H:%M:%S")

    instelling = Instelling.acieve_instelling()
    MELDINGEN_URL = (
        settings.MELDINGEN_URL if not instelling else instelling.mor_core_basis_url
    )
    TAAKR_URL = settings.TAAKR_URL if not instelling else instelling.taakr_basis_url

    return {
        "MELDINGEN_URL": MELDINGEN_URL,
        "UI_SETTINGS": settings.UI_SETTINGS,
        "DEBUG": settings.DEBUG,
        "DEV_SOCKET_PORT": settings.DEV_SOCKET_PORT,
        "GET": context.GET,
        "ABSOLUTE_ROOT": absolute(context).get("ABSOLUTE_ROOT"),
        "SESSION_EXPIRY_MAX_TIMESTAMP": session_expiry_max_timestamp,
        "SESSION_EXPIRY_TIMESTAMP": session_expiry_timestamp,
        "SESSION_CHECK_INTERVAL_SECONDS": settings.SESSION_CHECK_INTERVAL_SECONDS,
        "LOGOUT_URL": reverse("oidc_logout")
        if settings.OIDC_ENABLED
        else "/admin/logout/",
        "LOGIN_URL": f"{reverse('oidc_authentication_init')}?next={absolute(context).get('FULL_URL')}"
        if settings.OIDC_ENABLED
        else "/admin/login/",
        "GIT_SHA": settings.GIT_SHA,
        "APP_ENV": settings.APP_ENV,
        "TAAKR_URL": TAAKR_URL,
        "DEPLOY_DATE": deploy_date_formatted,
        "MOR_CORE_URL_PREFIX": settings.MOR_CORE_URL_PREFIX,
        "MOR_CORE_PROTECTED_URL_PREFIX": settings.MOR_CORE_PROTECTED_URL_PREFIX,
    }
