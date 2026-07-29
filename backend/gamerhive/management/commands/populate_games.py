from datetime import datetime, timezone as dt_timezone
import json

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify
from igdb.wrapper import IGDBWrapper

from gamerhive.environment import Settings
from gamerhive.models import BlockedCompany, Company, Game, Genre, Platform, QuarantinedGame

SKIP_SUMMARY_TERMS = ["mod", "romhack", "hack", "fanmade"]
SKIP_NAME_TERMS = ["randomizer"]
ADULT_TEXT_TERMS = ["hentai", "porn", "erotic", "nsfw", "sex", "adult only"]
ADULT_AGE_RATING_CODES = {12, 17, 22, 26, 33, 38, 39}


def get_platform_ids(families):
    if not families:
        return list(Platform.objects.values_list("igdb_platform_id", flat=True))
    ids = Platform.objects.filter(name__icontains=families[0]).values_list("igdb_platform_id", flat=True)
    for family in families[1:]:
        ids = list(ids) + list(
            Platform.objects.filter(name__icontains=family).values_list("igdb_platform_id", flat=True)
        )
    return ids


def _extract_names(items):
    return [item.get("name", "") for item in items if isinstance(item, dict)]


def _extract_company_rows(involved_companies):
    rows = []
    for item in involved_companies:
        if not isinstance(item, dict):
            continue
        company = item.get("company") or {}
        company_id = company.get("id")
        company_name = (company.get("name") or "").strip()
        if not company_id or not company_name:
            continue
        rows.append(
            {
                "id": company_id,
                "name": company_name,
                "developer": bool(item.get("developer")),
                "publisher": bool(item.get("publisher")),
            }
        )
    return rows


def should_skip_game(game_data, settings: Settings, blocked_company_names: set[str]):
    name = (game_data.get("name") or "").strip()
    summary = (game_data.get("summary") or "").strip()

    if not name:
        return "missing_name"
    if len(summary) < settings.igdb_min_summary_chars:
        return "summary_too_short"
    if not game_data.get("cover", {}).get("image_id"):
        return "missing_cover"
    if not game_data.get("first_release_date"):
        return "missing_release_date"
    if (game_data.get("total_rating_count") or 0) < settings.igdb_min_rating_count:
        return "low_rating_count"

    platform_objs = Platform.objects.filter(igdb_platform_id__in=game_data.get("platforms", []))
    if any(p.category == 5 for p in platform_objs):
        return "platform_category_blocked"

    lower_name = name.lower()
    lower_summary = summary.lower()
    if any(word in lower_name for word in SKIP_NAME_TERMS):
        return "blocked_name_term"
    if any(word in lower_summary for word in SKIP_SUMMARY_TERMS):
        return "blocked_summary_term"

    searchable = " ".join(
        [
            lower_name,
            lower_summary,
            " ".join(_extract_names(game_data.get("themes", []))).lower(),
            " ".join(_extract_names(game_data.get("keywords", []))).lower(),
        ]
    )
    if any(term in searchable for term in ADULT_TEXT_TERMS):
        return "adult_text_term"

    age_rating_codes = {
        rating.get("rating")
        for rating in game_data.get("age_ratings", [])
        if isinstance(rating, dict) and rating.get("rating") is not None
    }
    if age_rating_codes.intersection(ADULT_AGE_RATING_CODES):
        return "adult_age_rating"

    company_names = {
        row["name"].strip().lower()
        for row in _extract_company_rows(game_data.get("involved_companies", []))
    }
    if company_names.intersection(blocked_company_names):
        return "blocked_company"

    return None


def upsert_quarantine(game_data, reason: str):
    game_id = game_data.get("id")
    if game_id is None:
        return
    name = (game_data.get("name") or "")[: QuarantinedGame._meta.get_field("name").max_length]
    slug = slugify(game_data.get("slug") or name) or f"game-{game_id}"
    slug = slug[: QuarantinedGame._meta.get_field("slug").max_length]
    QuarantinedGame.objects.update_or_create(
        igdb_game_id=game_id,
        defaults={
            "name": name,
            "slug": slug,
            "reason": reason,
            "payload": game_data,
        },
    )


class Command(BaseCommand):
    help = "Populate Game model from IGDB with safety filters"

    def handle(self, *args, **options):
        settings = Settings.load()
        self.stdout.write("Connecting to IGDB...")
        self.igdb = IGDBWrapper(settings.igdb_client_id, settings.igdb_access_token)
        self.populate_games(settings)
        self.stdout.write(self.style.SUCCESS("Finished populating game data!"))

    def populate_games(self, settings: Settings):
        platform_ids = get_platform_ids(settings.igdb_platform_families)
        if not platform_ids:
            self.stdout.write(self.style.WARNING("No platform ids matched. Nothing to ingest."))
            return

        platform_ids_str = ", ".join(str(p) for p in platform_ids)
        existing_ids = set(
            Game.objects.exclude(igdb_game_id__isnull=True).values_list("igdb_game_id", flat=True)
        )
        blocked_company_names = {
            name.strip().lower()
            for name in BlockedCompany.objects.filter(is_active=True).values_list("name", flat=True)
            if name and name.strip()
        }

        game_query_template = f"""
        fields id,name,genres,platforms,cover.image_id,summary,slug,first_release_date,total_rating_count,age_ratings.rating,themes.name,keywords.name,involved_companies.developer,involved_companies.publisher,involved_companies.company.id,involved_companies.company.name;
        where platforms = ({platform_ids_str});
        sort popularity desc;
        limit {{limit}};
        offset {{offset}};
        """

        for offset in range(0, settings.igdb_total_games, settings.igdb_batch_size):
            self.stdout.write(f"Fetching games {offset + 1} to {offset + settings.igdb_batch_size}...")
            query = game_query_template.format(limit=settings.igdb_batch_size, offset=offset)
            response = self.igdb.api_request("games", query)
            data = self._decode_response(response)

            for g in data:
                game_id = g.get("id")
                if game_id is None:
                    continue
                if game_id in existing_ids:
                    continue

                skip_reason = should_skip_game(g, settings, blocked_company_names)
                if skip_reason:
                    upsert_quarantine(g, skip_reason)
                    continue

                name = (g.get("name") or "")[: Game._meta.get_field("name").max_length]
                slug = slugify(g.get("slug") or name)
                if not slug:
                    slug = f"game-{game_id}"
                slug = slug[: Game._meta.get_field("slug").max_length]
                if Game.objects.filter(slug=slug).exclude(igdb_game_id=game_id).exists():
                    upsert_quarantine(g, "duplicate_slug")
                    continue

                cover = g.get("cover", {})
                image_id = cover.get("image_id")
                cover_url = (
                    f"https://images.igdb.com/igdb/image/upload/t_cover_big/{image_id}.jpg"
                    if image_id
                    else None
                )
                release_ts = g.get("first_release_date")
                release_date = (
                    datetime.fromtimestamp(release_ts, tz=dt_timezone.utc)
                    if release_ts
                    else None
                )

                game_obj, _ = Game.objects.update_or_create(
                    igdb_game_id=game_id,
                    defaults={
                        "name": name,
                        "slug": slug,
                        "summary": g.get("summary"),
                        "story_line": g.get("storyline"),
                        "release_date": release_date,
                        "cover_url": cover_url,
                        "created_at": timezone.now(),
                        "updated_at": timezone.now(),
                    },
                )
                existing_ids.add(game_id)
                QuarantinedGame.objects.filter(igdb_game_id=game_id).delete()

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

                company_rows = _extract_company_rows(g.get("involved_companies", []))
                for row in company_rows:
                    company_obj, _ = Company.objects.update_or_create(
                        igdb_company_id=row["id"],
                        defaults={"name": row["name"][: Company._meta.get_field("name").max_length]},
                    )
                    if row["developer"]:
                        game_obj.developers.add(company_obj)
                    if row["publisher"]:
                        game_obj.publishers.add(company_obj)

                game_obj.save()

    def _decode_response(self, response):
        if isinstance(response, bytes):
            return json.loads(response.decode("utf-8"))
        return response
