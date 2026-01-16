from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify
from igdb.wrapper import IGDBWrapper
import os
import json

from gamerhive.models import Genre

CLIENT_ID = os.getenv("IGDB_CLIENT_ID")
ACCESS_TOKEN = os.getenv("IGDB_ACCESS_TOKEN")


class Command(BaseCommand):
    help = "Populate Genre model from IGDB"

    def handle(self, *args, **options):
        self.stdout.write("Connecting to IGDB...")
        self.igdb = IGDBWrapper(CLIENT_ID, ACCESS_TOKEN)
        self.populate_genres()
        self.stdout.write(self.style.SUCCESS("Finished populating genre data!"))

    def populate_genres(self):
        query = "fields id,name; limit 500;"
        response = self.igdb.api_request("genres", query)
        data = self._decode_response(response)
        for g in data:
            name = g.get("name")
            if not name:
                continue
            Genre.objects.update_or_create(
                igdb_genre_id=g.get("id"),
                defaults={
                    "name": name,
                    "slug": slugify(name),
                    "created_at": timezone.now(),
                    "updated_at": timezone.now(),
                },
            )

    def _decode_response(self, response):
        if isinstance(response, bytes):
            return json.loads(response.decode("utf-8"))
        return response
