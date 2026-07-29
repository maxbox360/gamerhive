# GamerHive

GamerHive is a social platform for people who love games. The project is focused on helping players discover titles, share opinions, build lists, and connect with others around what they play.

## Project goal

Build a video game community hub where people can:

- discover games worth playing
- track and organize games into lists
- write and read reviews
- find other players with similar taste
- make game conversation more fun and social

## Current state

Today, the app includes:

- a **Django + Django Ninja API** with game, genre, platform, and user endpoints
- a **Next.js frontend** with a searchable, filterable games catalog
- IGDB-powered data population commands for genres, platforms, games, and companies
- Docker-based local development with Postgres (and optional Redis cache configuration)

## Tech stack

- **Frontend:** Next.js 15, React 19, TypeScript, Elastic UI
- **Backend:** Django 5, Django Ninja
- **Database:** PostgreSQL
- **Infra/dev:** Docker Compose

## Setup for collaborators

### Prerequisites

- **Docker & Docker Compose** (for local dev environment)
- **Node.js 20+** (for frontend development)
- **Python 3.12** (for backend development)
- **Git**

### Getting started

1. **Clone the repo:**
   ```bash
   git clone https://github.com/yourusername/gamerhive.git
   cd gamerhive
   ```

2. **Create `.env` file** — run the setup script (handles IGDB token generation automatically):
   ```bash
   python setup_env.py
   ```

   This prompts you for:
   - Database credentials
   - Django secret key and superuser account
   - IGDB Client ID & Secret (gets access token for you)
   - Redis URL (optional)

   Or create manually with these variables:
   ```
   # Database
   POSTGRES_USER=gamerhive
   POSTGRES_PASSWORD=your_password
   POSTGRES_DB=gamerhive
   DB_HOST=db
   DB_PORT=5432

   # Django
   DJANGO_SECRET_KEY=your_secret_key
   DJANGO_SUPERUSER_USERNAME=admin
   DJANGO_SUPERUSER_EMAIL=admin@example.com
   DJANGO_SUPERUSER_PASSWORD=your_admin_password
   DEBUG=True

   # IGDB API (get from https://dev.twitch.tv/console/apps)
   IGDB_CLIENT_ID=your_client_id
   IGDB_ACCESS_TOKEN=your_access_token

   # Redis (optional)
   REDIS_URL=redis://redis:6379/1
   ```

3. **Start the dev environment:**
   ```bash
   docker compose up --build
   ```

   This starts:
   - Django API on `http://localhost:8000`
   - Next.js frontend on `http://localhost:3000`
   - PostgreSQL on `localhost:5433`
   - Redis on `localhost:6379`

4. **Verify everything is running:**
   - Frontend: `http://localhost:3000/games`
   - API docs: `http://localhost:8000/api/docs`
   - Django admin: `http://localhost:8000/admin`

### Local development (without Docker)

#### Backend (Django)

1. Install Python 3.12 and create a virtual env:
   ```bash
   python3.12 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```

3. Run migrations:
   ```bash
   cd backend
   python manage.py migrate
   ```

4. Create superuser:
   ```bash
   python manage.py createsuperuser
   ```

5. Start the server:
   ```bash
   python manage.py runserver
   ```

#### Frontend (Next.js)

1. Install Node 20+ and dependencies:
   ```bash
   cd frontend
   npm install --legacy-peer-deps
   ```

2. Set environment variables (`.env.local`):
   ```
   NEXT_PUBLIC_API_URL=http://localhost:8000
   INTERNAL_API_URL=http://localhost:8000
   ```

3. Start dev server:
   ```bash
   npm run dev
   ```

## Run locally (Docker)

1. Create/update your `.env` with required values (database + Django + IGDB + superuser vars).
2. Start everything:

```bash
docker compose up --build
```

3. App endpoints:
   - Frontend: `http://localhost:3000`
   - Backend API docs: `http://localhost:8000/api/docs`
   - Django admin: `http://localhost:8000/admin`

## Populate game data

After the backend is up and your IGDB credentials are set, run:

```bash
docker compose exec django python manage.py gamerhive_init
```

This runs the built-in population commands in order:

1. `populate_genres`
2. `populate_platforms`
3. `populate_games`
4. `populate_companies`

## API overview

Base path: `/api`

- `/api/games/games/` — paginated games list
- `/api/games/games/{slug}` — game details
- `/api/games/genres` — genres list
- `/api/games/platforms` — platforms list
- `/api/users/` — basic users list