import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get CLIENT_ID and CLIENT_SECRET from environment variables
CLIENT_ID = os.getenv("IGDB_CLIENT_ID")
print(f"CLIENT_ID: {CLIENT_ID}")
CLIENT_SECRET = os.getenv("IGDB_CLIENT_SECRET")
print(f"CLIENT_SECRET: {os.getenv('CLIENT_SECRET') is not None}")

def generate_token():
    url = "https://id.twitch.tv/oauth2/token"
    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "client_credentials"
    }

    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()  # Raise an error for bad status codes
        data = response.json()
        
        # Extract the access token
        access_token = data.get("access_token")
        expires_in = data.get("expires_in")  # Token validity in seconds

        print(f"Access Token: {access_token}")
        print(f"Expires In: {expires_in} seconds (~{expires_in // 3600} hours)")

        # Optionally save the token to a file for later use
        with open("igdb_token.json", "w") as token_file:
            json.dump(data, token_file, indent=4)
            print("Token saved to igdb_token.json")

    except requests.exceptions.RequestException as e:
        print(f"Error generating token: {e}")

if __name__ == "__main__":
    generate_token()