import json
from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from gamerhive.environment import Settings
from gamerhive.management.commands.populate_games import (
    get_platform_ids,
    should_skip_game,
)
from gamerhive.models import Game, Platform


def _platform(igdb_platform_id, name):
    return Platform.objects.create(
        igdb_platform_id=igdb_platform_id,
        name=name,
        slug=name.lower().replace(" ", "-"),
        created_at=timezone.now(),
        updated_at=timezone.now(),
    )


def _game(game_id, **overrides):
    data = {
        "id": game_id,
        "name": f"Game {game_id}",
        "genres": [],
        "platforms": [1],
        "cover": {"image_id": "abc123"},
        "summary": "A" * 50,
        "slug": f"game-{game_id}",
        "first_release_date": 1000000,
        "total_rating_count": 10,
        "age_ratings": [],
        "themes": [],
        "keywords": [],
        "involved_companies": [],
    }
    data.update(overrides)
    return data


class PlatformFamilyCoverageTests(TestCase):
    """The 'Nintendo' family name doesn't literally appear in the names IGDB
    uses for Wii, Wii U, GameCube, and Game Boy, so a naive substring match
    silently excluded major consoles from the ingestion query."""

    def setUp(self):
        self.wii = _platform(5, "Wii")
        self.gamecube = _platform(21, "Nintendo GameCube")
        self.wiiu = _platform(41, "Wii U")
        self.n64 = _platform(4, "Nintendo 64")
        self.switch = _platform(130, "Nintendo Switch")
        self.ps5 = _platform(167, "PlayStation 5")
        self.dreamcast = _platform(23, "Dreamcast")
        self.sg1000 = _platform(84, "SG-1000")
        self.genesis = _platform(29, "Sega Mega Drive/Genesis")
        self.supergrafx = _platform(128, "PC Engine SuperGrafx")
        self.turbografx = _platform(86, "TurboGrafx-16/PC Engine")
        self.xbox_series = _platform(169, "Xbox Series X|S")

    def test_nintendo_family_includes_consoles_without_nintendo_in_name(self):
        ids = get_platform_ids(("Nintendo",))
        self.assertIn(self.wii.igdb_platform_id, ids)
        self.assertIn(self.gamecube.igdb_platform_id, ids)
        self.assertIn(self.wiiu.igdb_platform_id, ids)
        self.assertIn(self.n64.igdb_platform_id, ids)
        self.assertIn(self.switch.igdb_platform_id, ids)

    def test_unrelated_family_is_not_matched(self):
        ids = get_platform_ids(("Nintendo",))
        self.assertNotIn(self.ps5.igdb_platform_id, ids)

    def test_unknown_family_falls_back_to_plain_substring(self):
        ids = get_platform_ids(("PlayStation",))
        self.assertIn(self.ps5.igdb_platform_id, ids)
        self.assertNotIn(self.wii.igdb_platform_id, ids)

    def test_sega_family_includes_consoles_without_sega_in_name(self):
        ids = get_platform_ids(("Sega",))
        self.assertIn(self.genesis.igdb_platform_id, ids)
        self.assertIn(self.dreamcast.igdb_platform_id, ids)
        self.assertIn(self.sg1000.igdb_platform_id, ids)
        self.assertNotIn(self.ps5.igdb_platform_id, ids)

    def test_turbografx_family_includes_supergrafx(self):
        ids = get_platform_ids(("TurboGrafx",))
        self.assertIn(self.turbografx.igdb_platform_id, ids)
        self.assertIn(self.supergrafx.igdb_platform_id, ids)
        self.assertNotIn(self.ps5.igdb_platform_id, ids)

    def test_xbox_family_is_covered_by_plain_substring_fallback(self):
        # Xbox naming is consistent in IGDB, so no alias entry is needed;
        # confirm the plain fallback still matches every Xbox platform.
        ids = get_platform_ids(("Xbox",))
        self.assertIn(self.xbox_series.igdb_platform_id, ids)
        self.assertNotIn(self.ps5.igdb_platform_id, ids)


class ShouldSkipGameTermMatchingTests(TestCase):
    """'mod' as a naive substring matched inside 'modes'/'mode', quarantining
    real games (Melee/Brawl/Ultimate all mention 'modes' in their summary)."""

    def setUp(self):
        self.settings = Settings(
            igdb_client_id="client-id",
            igdb_access_token="token",
        )

    def test_word_containing_blocked_substring_is_not_flagged(self):
        game = _game(
            1627,
            name="Super Smash Bros. Melee",
            summary=(
                "A crossover platform fighting game with various single-player "
                "modes alongside its multiplayer focus, spanning fifty "
                "characters and stages."
            ),
        )
        self.assertIsNone(should_skip_game(game, self.settings, set()))

    def test_standalone_blocked_term_is_still_flagged(self):
        game = _game(
            2,
            summary="A total conversion mod for a popular shooter, fifty levels long.",
        )
        self.assertEqual(
            should_skip_game(game, self.settings, set()), "blocked_summary_term"
        )

    def test_standalone_hack_term_is_still_flagged(self):
        game = _game(
            3,
            summary="A community-made hack of a classic platformer with new levels.",
        )
        self.assertEqual(
            should_skip_game(game, self.settings, set()), "blocked_summary_term"
        )


class PopulateGamesPaginationTests(TestCase):
    def setUp(self):
        _platform(1, "PC")
        self.settings = Settings(
            igdb_client_id="client-id",
            igdb_access_token="token",
            igdb_total_games=1000,
            igdb_batch_size=500,
        )

    def test_pagination_advances_and_offsets_are_distinct(self):
        seen_offsets = []

        def fake_request(request_func, endpoint, query, *, logger, **kwargs):
            offset = int(query.split("offset")[1].split(";")[0].strip())
            seen_offsets.append(offset)
            # Each batch returns distinct, non-overlapping IGDB ids.
            batch = [_game(offset + i) for i in range(500)]
            return json.dumps(batch).encode("utf-8")

        with (
            patch("gamerhive.environment.Settings.load", return_value=self.settings),
            patch(
                "gamerhive.management.commands.populate_games.igdb_request_with_retry",
                side_effect=fake_request,
            ),
            patch("gamerhive.management.commands.populate_games.IGDBWrapper"),
        ):
            call_command("populate_games")

        self.assertEqual(seen_offsets, [0, 500])
        # 1000 distinct fetched ids across two pages, none collapsed.
        self.assertEqual(Game.objects.count(), 1000)

    def test_duplicate_igdb_ids_across_pages_are_not_double_imported(self):
        def fake_request(request_func, endpoint, query, *, logger, **kwargs):
            # Simulate an unstable/overlapping sort returning the same id twice.
            return json.dumps([_game(1)]).encode("utf-8")

        with (
            patch("gamerhive.environment.Settings.load", return_value=self.settings),
            patch(
                "gamerhive.management.commands.populate_games.igdb_request_with_retry",
                side_effect=fake_request,
            ),
            patch("gamerhive.management.commands.populate_games.IGDBWrapper"),
        ):
            call_command("populate_games")

        self.assertEqual(Game.objects.filter(igdb_game_id=1).count(), 1)


class SkipReasonAggregationTests(TestCase):
    def setUp(self):
        _platform(1, "PC")
        self.settings = Settings(
            igdb_client_id="client-id",
            igdb_access_token="token",
            igdb_total_games=1,
            igdb_batch_size=500,
        )

    def test_summary_reports_aggregated_skip_reasons(self):
        stdout = StringIO()
        batch = [
            _game(1),
            _game(2, summary="too short"),
            _game(3, summary="too short"),
            _game(4, **{"cover": {}}),
        ]
        with (
            patch("gamerhive.environment.Settings.load", return_value=self.settings),
            patch(
                "gamerhive.management.commands.populate_games.igdb_request_with_retry",
                return_value=json.dumps(batch).encode("utf-8"),
            ),
            patch("gamerhive.management.commands.populate_games.IGDBWrapper"),
        ):
            call_command("populate_games", stdout=stdout)

        summary = stdout.getvalue()
        self.assertIn("imported=1", summary)
        self.assertIn("skipped=3", summary)
        self.assertIn("skip_reasons:", summary)
        self.assertIn("summary_too_short=2", summary)
        self.assertIn("missing_cover=1", summary)
