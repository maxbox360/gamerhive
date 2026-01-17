from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.utils import timezone


class Command(BaseCommand):
    help = "Run all GamerHive population commands in order"

    def handle(self, *args, **options):
        self.stdout.write("Starting GamerHive initialization...")

        call_command("populate_genres")
        call_command("populate_platforms")
        call_command("populate_games")
        call_command("populate_companies")
