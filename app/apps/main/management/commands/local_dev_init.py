from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import BaseCommand, call_command


class Command(BaseCommand):
    help = "DEV COMMAND: Fill databasse with a set of data for testing purposes"

    def handle(self, *args, **options):
        call_command("loaddata", "initial_data")
        # Fix the passwords of fixtures

        if settings.DEBUG:
            Gebruiker = get_user_model()
            for user in Gebruiker.objects.all():
                user.set_password(user.password)
                user.save()
