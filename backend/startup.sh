#!/bin/bash
# Azure App Service startup script for EcoBridge FastAPI backend
set -e

echo "==> EcoBridge Backend Startup"
echo "==> Working directory: $(pwd)"

# Create data directory for SQLite (Azure ephemeral storage)
mkdir -p /home/site/wwwroot/data

# Run migrations
echo "==> Running Alembic migrations..."
alembic upgrade head || python -m alembic upgrade head || true

# Start server
PORT="${PORT:-8000}"
echo "==> Starting server on port $PORT..."

if command -v gunicorn >/dev/null 2>&1; then
  echo "==> Starting with Gunicorn..."
  exec gunicorn src.main:app \
    --workers 2 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:$PORT \
    --timeout 120 \
    --keep-alive 5 \
    --log-level info
else
  echo "==> Starting with Uvicorn..."
  exec python -m uvicorn src.main:app --host 0.0.0.0 --port $PORT
fi
