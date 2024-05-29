from django.apps import AppConfig


class TakenConfig(AppConfig):
    name = "apps.taken"
    verbose_name = "Taken"

    def ready(self):
        import apps.taken.signal_receivers  # noqa
