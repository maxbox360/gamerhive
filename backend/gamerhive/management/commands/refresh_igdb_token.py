import os
from pathlib import Path

import requests
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Refresh IGDB token only when current token is invalid."

    def handle(self, *args, **options):
        client_id = getattr(settings, "IGDB_CLIENT_ID", "")
        client_secret = getattr(settings, "IGDB_CLIENT_SECRET", "")
        access_token = getattr(settings, "IGDB_ACCESS_TOKEN", "")

        self.stdout.write("Checking IGDB token...")
        if not client_id or not client_secret:
            raise CommandError(
                "IGDB_CLIENT_ID and IGDB_CLIENT_SECRET must be configured."
            )

        if access_token and self._token_is_valid(client_id, access_token):
            self.stdout.write("IGDB token is still valid. No update needed.")
            return

        self.stdout.write("IGDB token missing/expired. Generating a new token...")
        new_token = self._generate_token(client_id, client_secret)
        self._update_env_token(new_token)
        self._update_runtime_token(new_token)
        self.stdout.write(self.style.SUCCESS("IGDB token refreshed in .env."))

    def _token_is_valid(self, client_id: str, token: str) -> bool:
        response = requests.post(
            "https://api.igdb.com/v4/genres",
            headers={
                "Client-ID": client_id,
                "Authorization": f"Bearer {token}",
                "Content-Type": "text/plain",
            },
            data="fields id; limit 1;",
            timeout=15,
        )
        return response.ok

    def _generate_token(self, client_id: str, client_secret: str) -> str:
        response = requests.post(
            "https://id.twitch.tv/oauth2/token",
            data={
                "client_id": client_id,
                "client_secret": client_secret,
                "grant_type": "client_credentials",
            },
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()
        token = data.get("access_token")
        if not token:
            raise CommandError("Token response missing access_token.")
        return token

    def _update_env_token(self, new_token: str) -> None:
        env_candidates = (
            Path("/app/.env"),
            Path(__file__).resolve().parents[4] / ".env",
            Path.cwd() / ".env",
        )
        env_path = next((p for p in env_candidates if p.exists()), None)
        if env_path is None:
            raise CommandError(".env file not found.")

        lines = env_path.read_text().splitlines()
        for index, line in enumerate(lines):
            if line.startswith("IGDB_ACCESS_TOKEN="):
                lines[index] = f"IGDB_ACCESS_TOKEN={new_token}"
                break
        else:
            lines.append(f"IGDB_ACCESS_TOKEN={new_token}")
        env_path.write_text("\n".join(lines) + "\n")

    def _update_runtime_token(self, new_token: str) -> None:
        os.environ["IGDB_ACCESS_TOKEN"] = new_token
        settings.IGDB_ACCESS_TOKEN = new_token
