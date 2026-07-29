# Local Development (without Docker)

Run the frontend and backend separately without Docker. Useful if you want faster iteration or prefer local development.

## Prerequisites

First install:
- [Python 3.12](./INSTALLATION.md#python-312-for-backend-development)
- [Node.js 20+](./INSTALLATION.md#nodejs-for-frontend-development)
- [IGDB credentials](./IGDB_SETUP.md)

Then you can skip Docker and run both services locally.

---

## Backend (Django)

### 1. Set up virtual environment

```bash
cd backend
python3.12 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Your terminal should now show `(venv)`.

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure .env

Create `.env` in the `backend/` directory (or use the `setup_env.py` script from the root):

```bash
cd ..
python setup_env.py
```

Make sure these are set:
```
POSTGRES_USER=gamerhive
POSTGRES_PASSWORD=your_password
POSTGRES_DB=gamerhive
DB_HOST=localhost     # NOT 'db' — we're running locally
DB_PORT=5432

DJANGO_SECRET_KEY=your_secret_key
DEBUG=True

IGDB_CLIENT_ID=your_client_id
IGDB_ACCESS_TOKEN=your_access_token
```

### 4. Set up PostgreSQL

You need a running PostgreSQL database. Choose one:

**Option A: Docker container (easy)**

Run just the database:

```bash
docker run --name gamerhive-db \
  -e POSTGRES_USER=gamerhive \
  -e POSTGRES_PASSWORD=your_password \
  -e POSTGRES_DB=gamerhive \
  -p 5432:5432 \
  -d postgres:16
```

**Option B: Installed locally**

If you have PostgreSQL installed locally, create the database:

```bash
createdb -U postgres gamerhive
```

Then set your password in the database.

### 5. Run migrations

```bash
cd backend
python manage.py migrate
```

### 6. Create superuser

```bash
python manage.py createsuperuser
```

Enter a username, email, and password.

### 7. Start the Django server

```bash
python manage.py runserver
```

The API is now running on `http://localhost:8000`.

Check it out:
- API docs: http://localhost:8000/api/docs
- Django admin: http://localhost:8000/admin (use your superuser credentials)

---

## Frontend (Next.js)

### 1. Install dependencies

```bash
cd frontend
npm install --legacy-peer-deps
```

### 2. Create .env.local

Create `frontend/.env.local`:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
INTERNAL_API_URL=http://localhost:8000
```

### 3. Start the dev server

```bash
npm run dev
```

The frontend is now running on `http://localhost:3000`.

---

## Running both together

In two separate terminal windows:

**Terminal 1 (Backend):**
```bash
cd backend
source venv/bin/activate  # Or: venv\Scripts\activate (Windows)
python manage.py runserver
```

**Terminal 2 (Frontend):**
```bash
cd frontend
npm run dev
```

Visit http://localhost:3000 — it should connect to your local Django API at `http://localhost:8000`.

---

## Troubleshooting

### "Cannot connect to PostgreSQL"

- Is PostgreSQL running? If using Docker: `docker ps | grep postgres`
- Wrong password? Check your `.env` matches what you created
- Wrong port? Make sure `DB_PORT=5432` in `.env`

### "Module not found" errors in backend

- Are you in the right virtual environment? Check for `(venv)` in your terminal
- Did you run `pip install -r requirements.txt`? Try it again

### Frontend shows "Failed to fetch from API"

- Is Django running? Check `http://localhost:8000/api/docs`
- Is `.env.local` correctly set? Should be `NEXT_PUBLIC_API_URL=http://localhost:8000`
- Check your browser console for the exact error

### Changes aren't showing up

- **Django:** Restart `python manage.py runserver` after code changes
- **Next.js:** Restart `npm run dev` for some changes (CSS imports, env vars)

---

## Back to Docker?

When you're done with local development, you can go back to Docker:

```bash
docker compose down
docker compose up --build
```

---

[← Back to setup guide](./SETUP.md)
