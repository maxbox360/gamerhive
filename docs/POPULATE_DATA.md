# Populate Game Data

After you have GamerHive running, you'll want to load games into your library.

## What gets populated?

The `gamerhive_init` command runs these in order:

1. **Genres** — fetches game genres from IGDB
2. **Platforms** — fetches gaming platforms (PC, PlayStation, Xbox, etc.)
3. **Companies** — fetches game publishers and developers
4. **Games** — fetches 200,000+ games with ratings, release dates, cover art, etc.

## Automatic population (Docker)

When you first start GamerHive with Docker, the `django-init` service runs automatically:

```bash
docker compose up --build
```

This runs `gamerhive_init` once, then exits. The `django` service starts after init completes.

**Check the logs to see progress:**

```bash
docker compose logs django-init -f
```

Wait for output like:

```
Connecting to IGDB...
Fetching games 1 to 500...
Fetching games 501 to 1000...
...
✓ Population complete
```

Then visit http://localhost:3000/games to see the games in your library.

---

## Manual population (Local dev or Docker exec)

If you want to run it manually:

### Using Docker

```bash
docker compose exec django python manage.py gamerhive_init
```

### Local development

Make sure Django is running, then:

```bash
cd backend
source venv/bin/activate
python manage.py gamerhive_init
```

---

## Configuration

All population settings are in `backend/gamerhive/environment.py`:

| Setting | Default | What it does |
|---------|---------|------------|
| `IGDB_TOTAL_GAMES` | 200000 | Total games to fetch |
| `IGDB_BATCH_SIZE` | 500 | Games per API request |
| `IGDB_MIN_SUMMARY_CHARS` | 200 | Minimum game description length |
| `IGDB_MIN_RATING_COUNT` | 50 | Minimum number of ratings |
| `IGDB_PLATFORM_FAMILIES` | PC, PlayStation, Xbox, Nintendo | Platforms to include |

Override these in your `.env`:

```
IGDB_TOTAL_GAMES=50000      # Fetch only 50k games (faster)
IGDB_BATCH_SIZE=100         # Smaller batches (slower but safer)
IGDB_MIN_SUMMARY_CHARS=100  # Lower quality threshold
```

---

## Data quality

GamerHive filters out low-quality games automatically:

- **Too new:** Games with no release date
- **No cover:** Games without cover art
- **Incomplete:** Games with summary < 200 characters
- **Low ratings:** Games with < 50 ratings
- **Adult content:** Games tagged as adult (age rating 12, 17, 22, 26, 33, 38, 39)
- **Shovelware:** Games with terms like "asset", "pack", "bundle" in the name
- **Blocked companies:** Publishers/developers on the denylist

---

## Quarantine system

Games that are rejected during population go to the **QuarantinedGame** table. You can review them:

### Django admin

1. Go to http://localhost:8000/admin
2. Sign in with your superuser credentials
3. Look for **Quarantined games** in the Gamerhive section
4. Each entry shows:
   - Game name
   - Why it was rejected (reason)
   - Full IGDB payload (for inspection)

### Database query

```sql
SELECT name, reason, created_at FROM gamerhive_quarantinedgame
ORDER BY created_at DESC
LIMIT 20;
```

This lets you:
- Spot patterns (e.g., too many adult games filtered)
- Adjust thresholds if needed
- Manually review edge cases

---

## Population times

First run: ~5–10 minutes (fetches 200k games, writes to DB)

Subsequent runs: ~2–3 minutes (uses `update_or_create`, so duplicates are skipped)

Progress is logged to the console. Check `docker compose logs django-init -f` to monitor.

---

## Blocking a company

If a publisher or developer keeps shipping low-quality games, add them to the denylist:

### Via Django admin

1. Go to http://localhost:8000/admin
2. Sign in
3. Find **Blocked companies** in the Gamerhive section
4. Click **Add blocked company**
5. Enter company name and reason
6. Check **Is active**
7. Save

Next time you run `gamerhive_init`, games from that company will be quarantined instead of imported.

### Via database

```sql
INSERT INTO gamerhive_blockedcompany (name, reason, is_active, created_at)
VALUES ('Bad Publisher Inc', 'Shovelware and low-quality games', true, NOW());
```

---

## Troubleshooting

**Population takes forever**

- Check your internet connection
- Reduce `IGDB_TOTAL_GAMES` in `.env` (e.g., 50000 instead of 200000)
- Increase `IGDB_BATCH_SIZE` (e.g., 1000, up to 500 per request limit)

**"Error connecting to IGDB"**

- Check your `IGDB_ACCESS_TOKEN` is valid
- IGDB tokens expire every 60 days — regenerate with `python setup_env.py`
- Verify your internet connection

**Duplicate games in database**

- `gamerhive_init` uses `update_or_create`, so duplicates are automatically skipped
- Each game is keyed by IGDB ID, so running init twice is safe

**Too many adult games**

- Lower the `IGDB_MIN_RATING_COUNT` (adult games often have fewer ratings)
- Check the QuarantinedGame table to see what's being filtered
- Add publishers to BlockedCompany if they produce adult content

---

[← Back to setup guide](./SETUP.md)
