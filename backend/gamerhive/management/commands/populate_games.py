from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify
from igdb.wrapper import IGDBWrapper
import os
import json

from gamerhive.models import Game, Genre, Platform

CLIENT_ID = os.getenv("IGDB_CLIENT_ID")
ACCESS_TOKEN = os.getenv("IGDB_ACCESS_TOKEN")

# Configuration
TOTAL_GAMES = 20000 # total number of games to fetch
BATCH_SIZE = 500    # IGDB API max per request

def get_platform_ids(families=("PlayStation", "Xbox", "Nintendo", "Sega")):
    """Return a list of IGDB platform IDs for the specified families."""
    platform_ids = []
    for family in families:
        ids = Platform.objects.filter(name__icontains=family).values_list("igdb_platform_id", flat=True)
        platform_ids.extend(ids)
    return platform_ids

platform_ids = get_platform_ids()
platform_ids_str = ", ".join(str(p) for p in platform_ids)


# Queries
GENRE_QUERY = "fields id,name; limit 500;"
PLATFORM_QUERY = "fields id,name; limit 500;"
GAME_QUERY_TEMPLATE = f"""
fields id,name,genres,platforms,cover,summary,slug;
sort popularity desc;
where platforms = ({platform_ids_str});
limit {{limit}};
offset {{offset}};
"""

class Command(BaseCommand):
    help = "Populate Game, Genre, and Platform models from IGDB"

    def handle(self, *args, **options):
        self.stdout.write("Connecting to IGDB...")
        self.igdb = IGDBWrapper(CLIENT_ID, ACCESS_TOKEN)

        self.stdout.write("Populating genres...")
        self.populate_genres()

        self.stdout.write("Populating platforms...")
        self.populate_platforms()

        self.stdout.write("Populating games...")
        self.populate_games()

        self.stdout.write(self.style.SUCCESS("Finished populating IGDB data!"))

    def populate_genres(self):
        # Call IGDB /genres endpoint
        response = self.igdb.api_request("genres", GENRE_QUERY)
        data = self._decode_response(response)
        for g in data:
            name = g.get("name", "")
            if not name:
                continue
            Genre.objects.update_or_create(
                igdb_genre_id=g.get("id", None),
                defaults={
                    "name": name,
                    "slug": slugify(name),
                    "created_at": timezone.now(),
                    "updated_at": timezone.now(),
                }
            )

    def populate_platforms(self):
        # Call IGDB /platforms endpoint
        response = self.igdb.api_request("platforms", PLATFORM_QUERY)
        data = self._decode_response(response)
        for p in data:
            name = p.get("name", "")
            if not name:
                continue
            Platform.objects.update_or_create(
                igdb_platform_id=p.get("id", None),
                defaults={
                    "name": name,
                    "slug": slugify(name),
                    "abbreviation": p.get("abbreviation", ""),
                    "category": p.get("category", None),
                    "platform_type": p.get("platform_type", None),
                    "url": p.get("url", ""),
                    "created_at": timezone.now(),
                    "updated_at": timezone.now(),
                }
            )

    def populate_games(self):
        for offset in range(0, TOTAL_GAMES, BATCH_SIZE):
            self.stdout.write(f"Fetching games {offset + 1} to {offset + BATCH_SIZE}...")
            query = GAME_QUERY_TEMPLATE.format(limit=BATCH_SIZE, offset=offset)
            response = self.igdb.api_request("games", query)
            data = self._decode_response(response)

            for g in data:
                name = g.get("name", "")
                if not name:
                    continue
                base_slug = slugify(g.get("slug") or g.get("name", ""))
                slug = base_slug
                counter = 1
                while Game.objects.filter(slug=slug).exists():
                    slug = f"{base_slug}-{counter}"
                    counter += 1
                game_obj, _ = Game.objects.update_or_create(
                    igdb_game_id=g.get("id"),
                    defaults={
                        "name": name,
                        "slug": slug,
                        "summary": g.get("summary", ""),
                        "cover_id": g.get("cover"),
                        "created_at": timezone.now(),
                        "updated_at": timezone.now(),
                    }
                )

                # Assign M2M relationships
                for genre_id in g.get("genres", []):
                    try:
                        genre_obj = Genre.objects.get(igdb_genre_id=genre_id)
                        game_obj.genres.add(genre_obj)
                    except Genre.DoesNotExist:
                        continue

                for platform_id in g.get("platforms", []):
                    try:
                        platform_obj = Platform.objects.get(igdb_platform_id=platform_id)
                        game_obj.platforms.add(platform_obj)
                    except Platform.DoesNotExist:
                        continue

                game_obj.save()
        
    
    def _decode_response(self, response):
        """Convert bytes response to JSON-like list if needed"""
        if isinstance(response, bytes):
            import json
            return json.loads(response.decode("utf-8"))
        return response
