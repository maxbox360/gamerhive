import os
from unittest.mock import patch

from django.conf import settings
from django.core.management import call_command
from django.test import SimpleTestCase, override_settings


class RefreshIgdbTokenCommandTests(SimpleTestCase):
    @override_settings(
        IGDB_CLIENT_ID="client-id",
        IGDB_CLIENT_SECRET="client-secret",
        IGDB_ACCESS_TOKEN="expired-token",
    )
    def test_refresh_updates_runtime_token(self):
        with patch.dict(
            os.environ, {"IGDB_ACCESS_TOKEN": "expired-token"}, clear=False
        ), patch(
            "gamerhive.management.commands.refresh_igdb_token.Command._token_is_valid",
            return_value=False,
        ), patch(
            "gamerhive.management.commands.refresh_igdb_token.Command._generate_token",
            return_value="fresh-token",
        ), patch(
            "gamerhive.management.commands.refresh_igdb_token.Command._update_env_token"
        ):
            call_command("refresh_igdb_token")
            self.assertEqual(os.environ["IGDB_ACCESS_TOKEN"], "fresh-token")
            self.assertEqual(settings.IGDB_ACCESS_TOKEN, "fresh-token")
