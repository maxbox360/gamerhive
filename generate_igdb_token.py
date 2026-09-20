import os
import subprocess
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

ENV_FILE = Path(".env")
CLIENT_ID = os.getenv("IGDB_CLIENT_ID")
CLIENT_SECRET = os.getenv("IGDB_CLIENT_SECRET")
ACCESS_TOKEN = os.getenv("IGDB_ACCESS_TOKEN")


def token_is_valid(client_id: str, token: str) -> bool:
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


def generate_token(client_id: str, client_secret: str) -> str:
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
    access_token = data.get("access_token")
    if not access_token:
        raise RuntimeError("Token response missing access_token.")
    return access_token


def update_env_token(new_token: str) -> None:
    if not ENV_FILE.exists():
        raise RuntimeError(".env not found.")

    lines = ENV_FILE.read_text().splitlines()
    updated = False
    for i, line in enumerate(lines):
        if line.startswith("IGDB_ACCESS_TOKEN="):
            lines[i] = f"IGDB_ACCESS_TOKEN={new_token}"
            updated = True
            break
    if not updated:
        lines.append(f"IGDB_ACCESS_TOKEN={new_token}")

    ENV_FILE.write_text("\n".join(lines) + "\n")


def inject_into_docker() -> None:
    subprocess.run(
        ["docker", "compose", "up", "-d", "django", "django-init"],
        check=True,
    )


def main() -> None:
    if not CLIENT_ID or not CLIENT_SECRET:
        raise RuntimeError("IGDB_CLIENT_ID and IGDB_CLIENT_SECRET are required in .env")

    if ACCESS_TOKEN and token_is_valid(CLIENT_ID, ACCESS_TOKEN):
        print("IGDB token is still valid. No update needed.")
        return

    print("IGDB token missing/expired. Generating a new token...")
    new_token = generate_token(CLIENT_ID, CLIENT_SECRET)
    update_env_token(new_token)
    inject_into_docker()
    print("IGDB token refreshed and Docker services updated.")


if __name__ == "__main__":
    main()
