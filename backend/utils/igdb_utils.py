import os
import requests
from datetime import datetime, timezone

from django.conf import settings

def get_igdb_access_token():
    """
    Returns a valid IGDB access token, refreshing if expired or missing.
    """
    token = os.environ.get("IGDB_ACCESS_TOKEN")
    expires_at = os.environ.get("IGDB_TOKEN_EXPIRES_IN")

    if token and expires_at:
        expires_at_dt = datetime.fromisoformat(expires_at)
        now = datetime.now(timezone.utc)
        if now < expires_at_dt:
            # Token still valid
            return token

    # Token missing or expired -> refresh
    response = requests.post(
        "https://id.twitch.tv/oauth2/token",
        params={
            "client_id": settings.IGDB_CLIENT_ID,
            "client_secret": settings.IGDB_CLIENT_SECRET,
            "grant_type": "client_credentials"
        }
    )
    response.raise_for_status()
    data = response.json()

    token = data["access_token"]
    expires_in = data["expires_in"]  # seconds

    # Calculate exact expiration datetime
    expires_at_dt = datetime.utcnow() + timedelta(seconds=expires_in)

    # Save to environment (for current process)
    os.environ["IGDB_ACCESS_TOKEN"] = token
    os.environ["IGDB_TOKEN_EXPIRES_AT"] = expires_at_dt.isoformat()

    # Optional: persist to .env or database if you want across restarts

    return token
