from django.apps import AppConfig


class MainConfig(AppConfig):
    name = "apps.main"
    verbose_name = "Main"

    def ready(self):
        import apps.main.signal_receivers  # noqa
