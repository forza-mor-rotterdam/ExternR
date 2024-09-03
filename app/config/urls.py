from apps.aliassen.views import MeldingNotificatieAPIView
from apps.authenticatie.views import (
    GebruikerAanmakenView,
    GebruikerAanpassenView,
    GebruikerLijstView,
    GebruikerProfielView,
    gebruiker_bulk_import,
)
from apps.authorisatie.views import (
    RechtengroepAanmakenView,
    RechtengroepAanpassenView,
    RechtengroepLijstView,
    RechtengroepVerwijderenView,
)
from apps.beheer.views import beheer
from apps.context.views import (
    ContextAanmakenView,
    ContextAanpassenView,
    ContextLijstView,
    ContextVerwijderenView,
)
from apps.health.views import healthz
from apps.main.views import (
    clear_melding_token_from_cache,
    config,
    http_403,
    http_404,
    http_500,
    informatie,
    kaart_modus,
    meldingen_bestand,
    meldingen_bestand_protected,
    root,
    sorteer_filter,
    taak_afhandelen,
    taak_detail,
    taak_detail_melding_tijdlijn,
    taak_zoeken,
    taken,
    taken_filter,
    taken_lijst,
    ui_settings_handler,
)
from apps.taken.views import (
    TaaktypeAanmakenView,
    TaaktypeAanpassenView,
    TaaktypeLijstView,
    taak_feedback_handle,
)
from apps.taken.viewsets import TaaktypeViewSet, TaakViewSet
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
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
    path("informatie/", informatie, name="informatie"),
    path("api/v1/", include((router.urls, "app"), namespace="v1")),
    path(
        "api/v1/melding/",
        MeldingNotificatieAPIView.as_view(),
        name="melding_notificatie",
    ),
    path("api-token-auth/", views.obtain_auth_token),
    path(
        "admin/clear-melding-token-from-cache/",
        clear_melding_token_from_cache,
        name="clear_melding_token_from_cache",
    ),
    path("config/", config, name="config"),
    path("health/", include("health_check.urls")),
    path("healthz/", healthz, name="healthz"),
    # START taken
    path(
        "taken/",
        taken,
        name="taken",
    ),
    path(
        "taken/filter/",
        taken_filter,
        name="taken_filter",
    ),
    path(
        "taken/lijst/",
        taken_lijst,
        name="taken_lijst",
    ),
    # URL pattern for https://externr.forzamor.nl/taak-feedback-externe-instantie/{taak_id}/{email_hash}/
    path(
        "taak-feedback-externe-instantie/<int:taak_id>/<str:email_hash>/",
        taak_feedback_handle,
        name="feedback",
    ),
    path("sorteer-filter/", sorteer_filter, name="sorteer_filter"),
    path("taak-zoeken/", taak_zoeken, name="taak_zoeken"),
    path("kaart-modus/", kaart_modus, name="kaart_modus"),
    path("taak/<int:id>/", taak_detail, name="taak_detail"),
    path(
        "taak/<int:id>/melding-tijdlijn",
        taak_detail_melding_tijdlijn,
        name="taak_detail_melding_tijdlijn",
    ),
    # Gebruikers
    path(
        "gebruiker/profiel/",
        GebruikerProfielView.as_view(),
        name="gebruiker_profiel",
    ),
    # END taken
    # START partials
    path("part/pageheader-form/", ui_settings_handler, name="pageheader_form_part"),
    path(
        "taak/<int:id>/afhandelen/",
        taak_afhandelen,
        name="taak_afhandelen",
    ),
    # END partials
    # START beheer
    path("beheer/", beheer, name="beheer"),
    path("beheer/gebruiker/", GebruikerLijstView.as_view(), name="gebruiker_lijst"),
    path(
        "beheer/gebruiker/bulk-import/",
        gebruiker_bulk_import,
        name="gebruiker_bulk_import",
    ),
    path(
        "beheer/gebruiker/aanmaken/",
        GebruikerAanmakenView.as_view(),
        name="gebruiker_aanmaken",
    ),
    path(
        "beheer/gebruiker/<int:pk>/aanpassen/",
        GebruikerAanpassenView.as_view(),
        name="gebruiker_aanpassen",
    ),
    path("beheer/context/", ContextLijstView.as_view(), name="context_lijst"),
    path(
        "beheer/context/aanmaken/",
        ContextAanmakenView.as_view(),
        name="context_aanmaken",
    ),
    path(
        "beheer/context/<int:pk>/aanpassen/",
        ContextAanpassenView.as_view(),
        name="context_aanpassen",
    ),
    path(
        "beheer/context/<int:pk>/verwijderen/",
        ContextVerwijderenView.as_view(),
        name="context_verwijderen",
    ),
    path("beheer/taaktype/", TaaktypeLijstView.as_view(), name="taaktype_lijst"),
    path(
        "beheer/taaktype/aanmaken/",
        TaaktypeAanmakenView.as_view(),
        name="taaktype_aanmaken",
    ),
    path(
        "beheer/taaktype/<int:pk>/aanpassen/",
        TaaktypeAanpassenView.as_view(),
        name="taaktype_aanpassen",
    ),
    path(
        "beheer/rechtengroep/",
        RechtengroepLijstView.as_view(),
        name="rechtengroep_lijst",
    ),
    path(
        "beheer/rechtengroep/aanmaken/",
        RechtengroepAanmakenView.as_view(),
        name="rechtengroep_aanmaken",
    ),
    path(
        "beheer/rechtengroep/<int:pk>/aanpassen/",
        RechtengroepAanpassenView.as_view(),
        name="rechtengroep_aanpassen",
    ),
    path(
        "beheer/rechtengroep/<int:pk>/verwijderen/",
        RechtengroepVerwijderenView.as_view(),
        name="rechtengroep_verwijderen",
    ),
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
    re_path(r"core/media/", meldingen_bestand, name="meldingen_bestand"),
    re_path(
        r"core-protected/media/",
        meldingen_bestand_protected,
        name="meldingen_bestand_protected",
    ),
]

if settings.OIDC_ENABLED:
    urlpatterns += [
        path(
            "admin/login/",
            RedirectView.as_view(
                url="/oidc/authenticate/?next=/admin/",
                permanent=False,
            ),
            name="admin_login",
        ),
        path(
            "admin/logout/",
            RedirectView.as_view(
                url="/oidc/logout/?next=/admin/",
                permanent=False,
            ),
            name="admin_logout",
        ),
    ]

urlpatterns += [
    path("admin/", admin.site.urls),
    path("oidc/", include("mozilla_django_oidc.urls")),
]

if settings.APP_ENV != "productie":
    urlpatterns += [
        path("403/", http_403, name="403"),
        path("404/", http_404, name="404"),
        path("500/", http_500, name="500"),
    ]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [
        path("__debug__/", include("debug_toolbar.urls")),
    ]
