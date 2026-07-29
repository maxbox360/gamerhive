#!/usr/bin/env python3
import os
import sys
import json
import secrets
import requests
from pathlib import Path
from dotenv import load_dotenv

def get_input(prompt, default=None):
    """Get user input with optional default."""
    if default:
        prompt = f"{prompt} [{default}]: "
    else:
        prompt = f"{prompt}: "
    value = input(prompt).strip()
    return value if value else default

def generate_igdb_token(client_id, client_secret):
    """Generate IGDB access token using Twitch OAuth."""
    url = "https://id.twitch.tv/oauth2/token"
    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials"
    }
    
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        data = response.json()
        return data.get("access_token")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error generating token: {e}")
        return None

def setup_env():
    """Interactively set up .env file."""
    env_file = Path(".env")
    
    # Check if .env already exists
    if env_file.exists():
        overwrite = get_input(f"{env_file} already exists. Overwrite?", "n")
        if overwrite.lower() != "y":
            print("Skipping .env setup.")
            return
    
    print("\n=== GamerHive .env Setup ===\n")
    
    # Database
    print("📦 Database Configuration")
    db_user = get_input("PostgreSQL user", "gamerhive")
    db_password = get_input("PostgreSQL password", secrets.token_urlsafe(16))
    db_name = get_input("PostgreSQL database name", "gamerhive")
    db_host = get_input("Database host (Docker: use 'db')", "db")
    db_port = get_input("Database port", "5432")
    
    # Django
    print("\n🔐 Django Configuration")
    django_secret = get_input("Django SECRET_KEY", secrets.token_urlsafe(50))
    debug = get_input("DEBUG mode (True/False)", "True")
    
    # Superuser
    print("\n👤 Django Superuser")
    su_username = get_input("Superuser username", "admin")
    su_email = get_input("Superuser email", "admin@example.com")
    su_password = get_input("Superuser password", secrets.token_urlsafe(16))
    
    # IGDB
    print("\n🎮 IGDB API Configuration")
    print("   Get credentials at: https://dev.twitch.tv/console/apps")
    client_id = get_input("IGDB Client ID")
    if not client_id:
        print("❌ Client ID required.")
        return
    
    client_secret = get_input("IGDB Client Secret")
    if not client_secret:
        print("❌ Client Secret required.")
        return
    
    print("Generating IGDB access token...")
    access_token = generate_igdb_token(client_id, client_secret)
    if not access_token:
        print("❌ Failed to generate IGDB token.")
        return
    print(f"✓ Token generated")
    
    # Redis (optional)
    print("\n⚡ Redis Configuration (optional)")
    redis_url = get_input("Redis URL", "redis://redis:6379/1")
    
    # Build .env content
    env_content = f"""# Database
POSTGRES_USER={db_user}
POSTGRES_PASSWORD={db_password}
POSTGRES_DB={db_name}
DB_HOST={db_host}
DB_PORT={db_port}

# Django
DJANGO_SECRET_KEY={django_secret}
DEBUG={debug}

# Superuser
DJANGO_SUPERUSER_USERNAME={su_username}
DJANGO_SUPERUSER_EMAIL={su_email}
DJANGO_SUPERUSER_PASSWORD={su_password}

# IGDB API
IGDB_CLIENT_ID={client_id}
IGDB_ACCESS_TOKEN={access_token}

# Redis
REDIS_URL={redis_url}
"""
    
    # Write .env file
    env_file.write_text(env_content)
    print(f"\n✓ .env file created at {env_file}")
    print("\nYou can now run: docker compose up --build")

if __name__ == "__main__":
    try:
        setup_env()
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
