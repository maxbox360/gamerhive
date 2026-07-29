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

## 🚀 Quick start

👉 **[Read the setup guide](./docs/SETUP.md)** — 3 steps to get running in 10 minutes.

## Setup guides

- **[📋 Setup guide](./docs/SETUP.md)** — Quick start (recommended first read)
- **[⚙️ Installation](./docs/INSTALLATION.md)** — Download and install tools (Docker, Node, Python)
- **[🎮 IGDB API setup](./docs/IGDB_SETUP.md)** — Get your game data API credentials
- **[💻 Local development](./docs/LOCAL_DEVELOPMENT.md)** — Run backend & frontend without Docker
- **[📚 Populate data](./docs/POPULATE_DATA.md)** — Load games into your library

## API overview

Base path: `/api`

- `/api/games/games/` — paginated games list
- `/api/games/games/{slug}` — game details
- `/api/games/genres` — genres list
- `/api/games/platforms` — platforms list
- `/api/users/` — basic users list