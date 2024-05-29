from django.apps import AppConfig


class AliassenConfig(AppConfig):
    name = "apps.aliassen"
    verbose_name = "Aliassen"

    def ready(self):
        import apps.aliassen.signal_receivers  # noqa
