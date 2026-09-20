from datetime import datetime, timezone

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from gamerhive.api import api

from routers.games.models import Game, Genre, Platform


class SessionAuthenticationConfigurationTests(TestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)
        self.user = get_user_model().objects.create_user(
            username="session-user",
            email="session-user@example.com",
            password="S3curePass123!",
        )

    def test_csrf_bootstrap_sets_cookie(self):
        response = self.client.get("/api/auth/csrf")

        self.assertEqual(response.status_code, 200)
        self.assertIn("csrfToken", response.json())
        self.assertIn("csrftoken", response.cookies)

    def test_ninja_api_has_csrf_enabled(self):
        self.assertTrue(getattr(api, "csrf", False))

    def test_session_authentication_makes_user_available(self):
        self.client.force_login(self.user)

        response = self.client.get("/api/users/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.wsgi_request.user, self.user)
        self.assertEqual(response.json()[0]["id"], self.user.id)

    def test_protected_user_endpoint_requires_session(self):
        response = self.client.get("/api/users/")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(set(response.json().keys()), {"detail"})

    def test_public_game_endpoints_remain_accessible_without_session(self):
        games_response = self.client.get("/api/games/games/")
        genres_response = self.client.get("/api/games/genres")
        platforms_response = self.client.get("/api/games/platforms")

        self.assertEqual(games_response.status_code, 200)
        self.assertEqual(genres_response.status_code, 200)
        self.assertEqual(platforms_response.status_code, 200)

    @override_settings(ROOT_URLCONF="routers.games.tests.csrf_test_urls")
    def test_unsafe_requests_require_csrf_token(self):
        self.client.force_login(self.user)

        response = self.client.post(
            "/api/csrf-probe",
            data="{}",
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 403)

    @override_settings(ROOT_URLCONF="routers.games.tests.csrf_test_urls")
    def test_unsafe_requests_accept_valid_csrf_token(self):
        self.client.force_login(self.user)
        csrf_response = self.client.get("/api/auth/csrf")

        response = self.client.post(
            "/api/csrf-probe",
            data="{}",
            content_type="application/json",
            HTTP_X_CSRFTOKEN=csrf_response.json()["csrfToken"],
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"authenticated": True})


class GameDiscoveryOrderingTests(TestCase):
    """Default game discovery ordering is release date ascending (oldest first)."""

    def setUp(self):
        self.client = Client()
        now = datetime(2024, 1, 1, tzinfo=timezone.utc)
        self.genre = Genre.objects.create(
            igdb_genre_id=1,
            name="Fighting",
            slug="fighting",
            created_at=now,
            updated_at=now,
        )
        self.platform = Platform.objects.create(
            igdb_platform_id=1,
            name="Nintendo 64",
            slug="nintendo-64",
            created_at=now,
            updated_at=now,
        )

        def make_game(igdb_id, name, slug, release_date):
            game = Game.objects.create(
                igdb_game_id=igdb_id,
                name=name,
                slug=slug,
                release_date=release_date,
                created_at=now,
                updated_at=now,
            )
            game.genres.add(self.genre)
            game.platforms.add(self.platform)
            return game

        # Deliberately created out of chronological order so ordering isn't
        # accidentally satisfied by insertion/id order.
        self.ultimate = make_game(
            5,
            "Super Smash Bros. Ultimate",
            "smash-ultimate",
            datetime(2018, 12, 7, tzinfo=timezone.utc),
        )
        self.melee = make_game(
            2,
            "Super Smash Bros. Melee",
            "smash-melee",
            datetime(2001, 11, 21, tzinfo=timezone.utc),
        )
        self.original = make_game(
            1,
            "Super Smash Bros.",
            "smash-original",
            datetime(1999, 4, 26, tzinfo=timezone.utc),
        )
        self.brawl = make_game(
            3,
            "Super Smash Bros. Brawl",
            "smash-brawl",
            datetime(2008, 1, 31, tzinfo=timezone.utc),
        )
        self.wiiu = make_game(
            4,
            "Super Smash Bros. for Wii U",
            "smash-wiiu",
            datetime(2014, 11, 21, tzinfo=timezone.utc),
        )
        # Same release date, deterministic tie-break must fall back to id.
        self.same_date_a = make_game(
            10, "Tie Game A", "tie-game-a", datetime(2020, 6, 1, tzinfo=timezone.utc)
        )
        self.same_date_b = make_game(
            11, "Tie Game B", "tie-game-b", datetime(2020, 6, 1, tzinfo=timezone.utc)
        )
        # Missing release date must not error and must sort deterministically.
        self.no_date = make_game(12, "Undated Game", "undated-game", None)

    def _slugs(self, response):
        return [item["slug"] for item in response.json()["items"]]

    def test_search_results_are_chronological(self):
        response = self.client.get(
            "/api/games/games/", {"search": "Super Smash Bros", "page_size": 10}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            self._slugs(response),
            [
                "smash-original",
                "smash-melee",
                "smash-brawl",
                "smash-wiiu",
                "smash-ultimate",
            ],
        )

    def test_genre_filter_preserves_release_date_ordering(self):
        response = self.client.get(
            "/api/games/games/", {"genre": "Fighting", "page_size": 10}
        )

        self.assertEqual(response.status_code, 200)
        slugs = self._slugs(response)
        dated_slugs = [s for s in slugs if s != "undated-game"]
        self.assertEqual(
            dated_slugs,
            [
                "smash-original",
                "smash-melee",
                "smash-brawl",
                "smash-wiiu",
                "smash-ultimate",
                "tie-game-a",
                "tie-game-b",
            ],
        )

    def test_platform_filter_preserves_release_date_ordering(self):
        response = self.client.get(
            "/api/games/games/", {"platform": "Nintendo 64", "page_size": 10}
        )

        self.assertEqual(response.status_code, 200)
        slugs = self._slugs(response)
        dated_slugs = [s for s in slugs if s != "undated-game"]
        self.assertEqual(
            dated_slugs,
            [
                "smash-original",
                "smash-melee",
                "smash-brawl",
                "smash-wiiu",
                "smash-ultimate",
                "tie-game-a",
                "tie-game-b",
            ],
        )

    def test_same_release_date_is_ordered_deterministically_by_id(self):
        response = self.client.get(
            "/api/games/games/", {"search": "Tie Game", "page_size": 10}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self._slugs(response), ["tie-game-a", "tie-game-b"])

    def test_missing_release_date_does_not_error_and_sorts_last(self):
        response = self.client.get(
            "/api/games/games/", {"genre": "Fighting", "page_size": 10}
        )

        self.assertEqual(response.status_code, 200)
        slugs = self._slugs(response)
        self.assertEqual(slugs[-1], "undated-game")

    def test_pagination_is_correct_with_release_date_ordering(self):
        page_one = self.client.get(
            "/api/games/games/", {"genre": "Fighting", "page": 1, "page_size": 3}
        )
        page_two = self.client.get(
            "/api/games/games/", {"genre": "Fighting", "page": 2, "page_size": 3}
        )

        self.assertEqual(page_one.status_code, 200)
        self.assertEqual(page_two.status_code, 200)
        self.assertEqual(
            self._slugs(page_one), ["smash-original", "smash-melee", "smash-brawl"]
        )
        self.assertEqual(
            self._slugs(page_two), ["smash-wiiu", "smash-ultimate", "tie-game-a"]
        )
        self.assertEqual(page_one.json()["total"], 8)
        self.assertEqual(page_one.json()["total_pages"], 3)
