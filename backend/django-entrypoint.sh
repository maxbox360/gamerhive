#!/bin/bash
set -e

echo "Waiting for Postgres to be ready..."

# Wait for Postgres
python - <<END
import time
import psycopg
import os

db_host = os.environ.get("DB_HOST", "db")
db_port = int(os.environ.get("DB_PORT", 5432))
db_name = os.environ.get("POSTGRES_DB")
db_user = os.environ.get("POSTGRES_USER")
db_pass = os.environ.get("POSTGRES_PASSWORD")

while True:
    try:
        conn = psycopg.connect(host=db_host, port=db_port, dbname=db_name, user=db_user, password=db_pass)
        conn.close()
        break
    except Exception:
        print("Postgres not ready yet, sleeping 1s...")
        time.sleep(1)

print("Postgres is ready!")
END

echo "Running migrations..."
python manage.py migrate

echo "Creating superuser if needed..."
python init_superuser.py

echo "Starting Django server..."
exec python manage.py runserver 0.0.0.0:8000

