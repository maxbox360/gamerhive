# IGDB API Setup

GamerHive uses the **IGDB API** to fetch game data, reviews, genres, platforms, and more. You'll need free Twitch developer credentials.

## Step 1: Create a Twitch account

If you don't have one already:

👉 **[Sign up at Twitch.tv](https://www.twitch.tv/login)**

(You can use any email. No streaming required.)

## Step 2: Register a developer application

Once logged in to Twitch:

1. Go to **[Twitch Developer Console](https://dev.twitch.tv/console/apps)**
2. Click **"Create Application"**
3. Fill in:
   - **Application Name:** GamerHive (or whatever you prefer)
   - **Application Category:** Select "Application Integration"
   - Check the terms and click **"Create"**

## Step 3: Get your credentials

You now have a developer app. You need two pieces:

1. **Client ID** — visible on the app details page
2. **Client Secret** — click "Manage" on your app, then "Generate a New Secret"

Copy both of these values somewhere safe (notepad is fine for now).

## Step 4: Generate your access token

This is the token GamerHive uses to call the IGDB API. The setup script does this automatically:

```bash
python setup_env.py
```

When prompted:
- **Paste your Client ID**
- **Paste your Client Secret**
- The script exchanges these for an **access token** and saves it to `.env`

That's it! Your `.env` file is now ready with:
```
IGDB_CLIENT_ID=your_client_id
IGDB_ACCESS_TOKEN=your_access_token
```

---

## What happens behind the scenes?

1. `setup_env.py` takes your Client ID and Client Secret
2. It calls Twitch OAuth API (`https://id.twitch.tv/oauth2/token`)
3. Twitch returns an **access token** (valid for ~60 days)
4. The script saves this token to `.env` so GamerHive can use it

Your Client Secret is **not saved** to `.env` — it's only used once to get the token.

---

## Token expiration

IGDB access tokens expire after ~60 days. When it expires:

1. Go back to [Twitch Developer Console](https://dev.twitch.tv/console/apps)
2. Click your app → "Manage"
3. Generate a new Client Secret
4. Run `python setup_env.py` again to get a fresh token

Or manually update `IGDB_ACCESS_TOKEN` in `.env` if you prefer.

---

## Troubleshooting

**"Error generating token" when running setup_env.py**

- Double-check your Client ID and Secret are copied exactly (no extra spaces)
- Verify your Twitch account email is confirmed
- Make sure your app is created successfully in the console

**Still stuck?**

- Check [IGDB API docs](https://api-docs.igdb.com/#getting-started)
- See [Twitch OAuth docs](https://dev.twitch.tv/docs/authentication)

---

[← Back to setup guide](./SETUP.md)
