from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify
from igdb.wrapper import IGDBWrapper
import json

from gamerhive.models import Game, Genre, Platform, Company
from gamerhive.environment import Settings

SKIP_SUMMARY_TERMS = ["mod", "romhack", "hack", "fanmade"]
SKIP_NAME_TERMS = ["randomizer"]


def get_platform_ids(families):
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
        settings = Settings.load()
        self.stdout.write("Connecting to IGDB...")
        self.igdb = IGDBWrapper(settings.igdb_client_id, settings.igdb_access_token)
        self.populate_games(settings)
        self.stdout.write(self.style.SUCCESS("Finished populating game data!"))


    def populate_games(self, settings: Settings):
        platform_ids_str = ", ".join(str(p) for p in get_platform_ids(settings.igdb_platform_families))
        existing_ids = set(
            Game.objects.exclude(igdb_game_id__isnull=True).values_list("igdb_game_id", flat=True)
        )
        GAME_QUERY_TEMPLATE = f"""
        fields id,name,genres,platforms,cover.image_id,summary,slug;
        where platforms = ({platform_ids_str});
        sort popularity desc;
        limit {{limit}};
        offset {{offset}};
        """

        for offset in range(0, settings.igdb_total_games, settings.igdb_batch_size):
            self.stdout.write(f"Fetching games {offset + 1} to {offset + settings.igdb_batch_size}...")
            query = GAME_QUERY_TEMPLATE.format(limit=settings.igdb_batch_size, offset=offset)
            response = self.igdb.api_request("games", query)
            data = self._decode_response(response)

            for g in data:
                if g.get("id") in existing_ids:
                    continue

                if should_skip_game(g):
                    continue
                

                name = (g.get("name") or "")[: Game._meta.get_field("name").max_length]
                slug = slugify(g.get("slug") or name)
                if not slug:
                    slug = f"game-{g.get('id')}"
                slug = slug[: Game._meta.get_field("slug").max_length]
                if Game.objects.filter(slug=slug).exclude(igdb_game_id=g.get("id")).exists():
                    continue
                cover = g.get("cover", {})
                image_id = cover.get("image_id")
                cover_url = f"https://images.igdb.com/igdb/image/upload/t_cover_big/{image_id}.jpg" if image_id else None

                game_obj, _ = Game.objects.update_or_create(
                    igdb_game_id=g.get("id"),
                    defaults={
                        "name": name,
                        "slug": slug,
                        "summary": g.get("summary"),
                        "story_line": g.get("storyline"),
                        "cover_url": cover_url,
                        "created_at": timezone.now(),
                        "updated_at": timezone.now(),
                    },
                )
                existing_ids.add(g.get("id"))

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

                # --- Fetch developer/publisher ---
                involved_companies_ids = g.get("involved_companies", [])
                if involved_companies_ids:
                    ics = self.get_involved_companies(involved_companies_ids)

                    dev_ids = [ic['company'] for ic in ics if ic.get('developer')]
                    pub_ids = [ic['company'] for ic in ics if ic.get('publisher')]

                    dev_companies = self.get_companies_by_ids(dev_ids)
                    pub_companies = self.get_companies_by_ids(pub_ids)

                    # --- Update M2M for developers ---
                    for c in dev_companies:
                        company_obj, _ = Company.objects.update_or_create(
                            igdb_company_id=c['id'],
                            defaults={'name': c['name']}
                        )
                        game_obj.developers.add(company_obj)

                    # --- Update M2M for publishers ---
                    for c in pub_companies:
                        company_obj, _ = Company.objects.update_or_create(
                            igdb_company_id=c['id'],
                            defaults={'name': c['name']}
                        )
                        game_obj.publishers.add(company_obj)

                game_obj.save()

    def _decode_response(self, response):
        if isinstance(response, bytes):
            return json.loads(response.decode("utf-8"))
        return response
