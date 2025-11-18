from apps.aliassen.views import MeldingNotificatieAPIView
from apps.authenticatie.views import GebruikerProfielView, LoginView, LogoutView
from apps.health.views import healthz
from apps.main.views import (
    http_403,
    http_404,
    http_500,
    prometheus_django_metrics,
    root,
    ui_settings_handler,
)
from apps.taken.views import taak_feedback_handle
from apps.taken.viewsets import TaaktypeViewSet, TaakViewSet
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework.authtoken import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"taak", TaakViewSet, basename="taak")
router.register(r"taaktype", TaaktypeViewSet, basename="taaktype")

urlpatterns = [
    path("", root, name="root"),
    path(
        "login/",
        LoginView.as_view(),
        name="login",
    ),
    path(
        "logout/",
        LogoutView.as_view(),
        name="logout",
    ),
    path("api/v1/", include((router.urls, "app"), namespace="v1")),
    path(
        "api/v1/melding/",
        MeldingNotificatieAPIView.as_view(),
        name="melding_notificatie",
    ),
    path("api-token-auth/", views.obtain_auth_token),
    path("health/", include("health_check.urls")),
    path("healthz/", healthz, name="healthz"),
    # START taken
    # URL pattern for https://externr.forzamor.nl/taak-feedback-externe-instantie/{taak_id}/{email_hash}/
    path(
        "taak-feedback-externe-instantie/<int:taak_id>/<str:email_hash>/",
        taak_feedback_handle,
        name="feedback",
    ),
    # Gebruikers
    path(
        "gebruiker/profiel/",
        GebruikerProfielView.as_view(),
        name="gebruiker_profiel",
    ),
    # END taken
    path("part/pageheader-form/", ui_settings_handler, name="pageheader_form_part"),
    # START beheer
    path("beheer/", include("apps.beheer.urls")),
    # END beheer
    path("api/schema/", SpectacularAPIView.as_view(api_version="v1"), name="schema"),
    # Optional UI:
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
    path("metrics", prometheus_django_metrics, name="prometheus_django_metrics"),
]

if not settings.ENABLE_DJANGO_ADMIN_LOGIN:
    urlpatterns += [
        path(
            "admin/login/",
            RedirectView.as_view(url="/login/?next=/admin/"),
            name="admin_login",
        ),
        path(
            "admin/logout/",
            RedirectView.as_view(url="/logout/?next=/"),
            name="admin_logout",
        ),
    ]

if settings.OIDC_ENABLED:
    urlpatterns += [
        path("oidc/", include("mozilla_django_oidc.urls")),
    ]

urlpatterns += [
    path("admin/", admin.site.urls),
]

if settings.APP_ENV != "productie":
    urlpatterns += [
        path("403/", http_403, name="403"),
        path("404/", http_404, name="404"),
        path("500/", http_500, name="500"),
    ]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += [
        path("__debug__/", include("debug_toolbar.urls")),
    ]
