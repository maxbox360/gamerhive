from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = "Run all GamerHive population commands in order"

    def handle(self, *args, **options):
        self.stdout.write("Starting GamerHive initialization...")
        self.stdout.write("Refreshing IGDB token...")
        call_command("refresh_igdb_token")

        self.stdout.write("Populating genres...")
        call_command("populate_genres")
        self.stdout.write("Populating platforms...")
        call_command("populate_platforms")
        self.stdout.write("Populating games...")
        call_command("populate_games")
        self.stdout.write("Populating companies...")
        call_command("populate_companies")
        self.stdout.write(self.style.SUCCESS("GamerHive initialization complete."))
