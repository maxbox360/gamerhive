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