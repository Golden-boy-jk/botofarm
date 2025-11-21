#!/bin/sh
set -e

echo "👉 Applying database migrations..."
alembic upgrade head

echo "✅ Migrations applied, starting app..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
