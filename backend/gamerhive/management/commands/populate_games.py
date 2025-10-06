from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify
from igdb.wrapper import IGDBWrapper
import os
import json

from gamerhive.models import Game, Genre, Platform

CLIENT_ID = os.getenv("IGDB_CLIENT_ID")
ACCESS_TOKEN = os.getenv("IGDB_ACCESS_TOKEN")
TOTAL_GAMES = 20000
BATCH_SIZE = 500

SKIP_SUMMARY_TERMS = ["mod", "romhack", "hack", "fanmade"]
SKIP_NAME_TERMS = ["randomizer"]
PLATFORM_FAMILIES = ("PlayStation", "Xbox", "Nintendo", "Sega")


def get_platform_ids(families=PLATFORM_FAMILIES):
    ids = Platform.objects.filter(
        name__icontains=families[0]  # will chain below
    ).values_list("igdb_platform_id", flat=True)
    for family in families[1:]:
        ids = list(ids) + list(
            Platform.objects.filter(name__icontains=family).values_list(
                "igdb_platform_id", flat=True
            )
        )
    return ids


def create_unique_slug(name):
    base_slug = slugify(name)
    slug = base_slug
    counter = 1
    while Game.objects.filter(slug=slug).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1
    return slug


def should_skip_game(game_data):
    name = game_data.get("name", "")
    summary = game_data.get("summary", "")
    if not name or not summary:
        return True

    # Skip based on platform category
    platform_objs = Platform.objects.filter(
        igdb_platform_id__in=game_data.get("platforms", [])
    )
    if any(p.category == 5 for p in platform_objs):
        return True

    # Skip by banned words
    if any(word.lower() in name.lower() for word in SKIP_NAME_TERMS):
        return True
    if any(word.lower() in summary.lower() for word in SKIP_SUMMARY_TERMS):
        return True

    return False


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
        query = "fields id,name; limit 500;"
        response = self.igdb.api_request("genres", query)
        data = self._decode_response(response)
        for g in data:
            name = g.get("name", "")
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

    def populate_games(self):
        platform_ids_str = ", ".join(str(p) for p in get_platform_ids())
        GAME_QUERY_TEMPLATE = f"""
        fields id,name,genres,platforms,cover,summary,slug;
        where platforms = ({platform_ids_str});
        sort popularity desc;
        limit {{limit}};
        offset {{offset}};
        """

        for offset in range(0, TOTAL_GAMES, BATCH_SIZE):
            self.stdout.write(f"Fetching games {offset + 1} to {offset + BATCH_SIZE}...")
            query = GAME_QUERY_TEMPLATE.format(limit=BATCH_SIZE, offset=offset)
            response = self.igdb.api_request("games", query)
            data = self._decode_response(response)

            for g in data:
                if should_skip_game(g):
                    continue

                slug = create_unique_slug(g.get("slug") or g.get("name"))
                game_obj, _ = Game.objects.update_or_create(
                    igdb_game_id=g.get("id"),
                    defaults={
                        "name": g.get("name"),
                        "slug": slug,
                        "summary": g.get("summary"),
                        "cover_id": g.get("cover"),
                        "created_at": timezone.now(),
                        "updated_at": timezone.now(),
                    },
                )

                # Assign M2M
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
        if isinstance(response, bytes):
            return json.loads(response.decode("utf-8"))
        return response
