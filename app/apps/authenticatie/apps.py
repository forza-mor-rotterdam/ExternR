from django.apps import AppConfig


class AuthenticatieConfig(AppConfig):
    name = "apps.authenticatie"
    verbose_name = "Authenticatie"

    def ready(self):
        import apps.authenticatie.signal_receivers  # noqa
