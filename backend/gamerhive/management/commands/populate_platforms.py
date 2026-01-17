from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify
from igdb.wrapper import IGDBWrapper
import os
import json

from gamerhive.models import Platform

CLIENT_ID = os.getenv("IGDB_CLIENT_ID")
ACCESS_TOKEN = os.getenv("IGDB_ACCESS_TOKEN")


class Command(BaseCommand):
    help = "Populate Platform model from IGDB"

    def handle(self, *args, **options):
        self.stdout.write("Connecting to IGDB...")
        self.igdb = IGDBWrapper(CLIENT_ID, ACCESS_TOKEN)
        self.populate_platforms()
        self.stdout.write(self.style.SUCCESS("Finished populating platform data!"))

    def populate_platforms(self):
        query = "fields id,name; limit 500;"
        response = self.igdb.api_request("platforms", query)
        data = self._decode_response(response)
        for p in data:
            name = p.get("name", "")
            if not name:
                continue
            Platform.objects.update_or_create(
                igdb_platform_id=p.get("id"),
                defaults={
                    "name": name,
                    "slug": slugify(name),
                    "abbreviation": p.get("abbreviation", ""),
                    "category": p.get("category"),
                    "platform_type": p.get("platform_type"),
                    "url": p.get("url", ""),
                    "created_at": timezone.now(),
                    "updated_at": timezone.now(),
                },
            )

    def _decode_response(self, response):
        if isinstance(response, bytes):
            return json.loads(response.decode("utf-8"))
        return response
