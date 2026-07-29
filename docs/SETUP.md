# Setup for collaborators

## Quick start (3 steps)

### 1️⃣ Install prerequisites

- **[Docker Desktop](https://www.docker.com/products/docker-desktop)** (for local dev environment)
- **[Node.js 20+](https://nodejs.org/)** (for frontend development)
- **[Python 3.12](https://www.python.org/downloads/)** (for backend development)
- **Git**

See [detailed installation guide](./INSTALLATION.md) for help with each tool.

### 2️⃣ Set up IGDB API credentials

GamerHive uses the IGDB API to populate game data. You'll need a free Twitch developer account.

**[👉 Follow the IGDB setup guide](./IGDB_SETUP.md)** — it handles everything including automatic token generation.

### 3️⃣ Start the dev environment

Clone the repo:
```bash
git clone https://github.com/yourusername/gamerhive.git
cd gamerhive
```

Run the environment setup script:
```bash
python setup_env.py
```

This creates your `.env` file with all required credentials (it uses the IGDB token you generated in step 2).

Start Docker:
```bash
docker compose up --build
```

**Verify everything is running:**
- Frontend: http://localhost:3000/games
- API docs: http://localhost:8000/api/docs
- Django admin: http://localhost:8000/admin (use credentials from setup script)

---

## What's running

- **Django API** on `http://localhost:8000`
- **Next.js frontend** on `http://localhost:3000`
- **PostgreSQL** on `localhost:5433`
- **Redis** on `localhost:6379` (optional cache)

---

## Troubleshooting

**Docker won't start?**
- Make sure Docker Desktop is running
- Check that ports 3000, 8000, 5433, 6379 aren't already in use

**IGDB token generation failed?**
- Verify your Client ID and Secret are correct
- Check that your Twitch account is confirmed (check email)
- Try running `setup_env.py` again

**Database errors?**
- The `django-init` service runs migrations automatically on first start
- If you need to reset, remove the Docker volumes: `docker compose down -v` then `docker compose up`

---

## Next steps

- [Local development without Docker](./LOCAL_DEVELOPMENT.md) — if you want to run backend/frontend separately
- [Populate game data](./POPULATE_DATA.md) — after setup, load games into your library
- Back to [main README](../README.md)
