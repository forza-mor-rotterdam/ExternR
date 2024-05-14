from django.apps import AppConfig
from health_check.plugins import plugin_dir


class ServicesConfig(AppConfig):
    name = "apps.health"
    verbose_name = "Health"

    def ready(self):
        from apps.health.custom_checks import MeldingenTokenCheck

        plugin_dir.register(MeldingenTokenCheck)
