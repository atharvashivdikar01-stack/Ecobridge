#!/bin/bash
# Azure App Service startup script for EcoBridge FastAPI backend
set -e

echo "==> EcoBridge Backend Startup"
echo "==> Working directory: $(pwd)"

# Create data directory for SQLite (Azure ephemeral storage)
mkdir -p /home/site/wwwroot/data

# Run migrations
echo "==> Running Alembic migrations..."
alembic upgrade head || true

# Start Gunicorn with Uvicorn workers (Azure App Service standard)
echo "==> Starting server..."
PORT="${PORT:-8000}"
exec gunicorn src.main:app \
  --workers 2 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:$PORT \
  --timeout 120 \
  --keep-alive 5 \
  --log-level info
