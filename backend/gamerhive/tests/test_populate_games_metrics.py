import json
from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from gamerhive.environment import Settings
from gamerhive.models import Game, Platform, QuarantinedGame


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


class PopulateGamesMetricsTests(TestCase):
    def setUp(self):
        Platform.objects.create(
            igdb_platform_id=1,
            name="PC",
            slug="pc",
            created_at=timezone.now(),
            updated_at=timezone.now(),
        )
        self.settings = Settings(
            igdb_client_id="client-id",
            igdb_access_token="token",
            igdb_total_games=1,
            igdb_batch_size=500,
        )

    def _run(self, batch):
        with (
            patch("gamerhive.environment.Settings.load", return_value=self.settings),
            patch(
                "gamerhive.management.commands.populate_games.igdb_request_with_retry",
                return_value=json.dumps(batch).encode("utf-8"),
            ),
            patch("gamerhive.management.commands.populate_games.IGDBWrapper"),
        ):
            call_command("populate_games")

    def test_successful_import_increments_imported_only(self):
        self._run([_game(1)])
        self.assertEqual(Game.objects.count(), 1)
        self.assertEqual(QuarantinedGame.objects.count(), 0)

    def test_skipped_record_does_not_increment_imported(self):
        self._run([_game(2, summary="too short")])
        self.assertEqual(Game.objects.count(), 0)
        self.assertEqual(QuarantinedGame.objects.count(), 1)
        self.assertEqual(QuarantinedGame.objects.get().reason, "summary_too_short")

    def test_existing_record_is_not_recounted_as_imported(self):
        Game.objects.create(
            igdb_game_id=3,
            name="Existing",
            slug="existing-3",
            created_at=timezone.now(),
            updated_at=timezone.now(),
        )
        self._run([_game(3)])
        # Untouched: should not be re-created/re-imported or quarantined.
        self.assertEqual(Game.objects.filter(igdb_game_id=3).count(), 1)
        self.assertEqual(QuarantinedGame.objects.count(), 0)

    def test_final_summary_reports_distinct_totals(self):
        Game.objects.create(
            igdb_game_id=3,
            name="Existing",
            slug="existing-3",
            created_at=timezone.now(),
            updated_at=timezone.now(),
        )
        stdout = StringIO()

        with (
            patch("gamerhive.environment.Settings.load", return_value=self.settings),
            patch(
                "gamerhive.management.commands.populate_games.igdb_request_with_retry",
                return_value=json.dumps(
                    [_game(1), _game(2, summary="too short"), _game(3)]
                ).encode("utf-8"),
            ),
            patch("gamerhive.management.commands.populate_games.IGDBWrapper"),
        ):
            call_command("populate_games", stdout=stdout)

        summary = stdout.getvalue()
        self.assertIn("fetched=3", summary)
        self.assertIn("imported=1", summary)
        self.assertIn("existing=1", summary)
        self.assertIn("skipped=1", summary)
