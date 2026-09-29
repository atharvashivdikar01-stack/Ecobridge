#!/bin/bash
# Azure App Service startup script for EcoBridge FastAPI backend
set -e

echo "==> EcoBridge Backend Startup"
echo "==> Working directory: $(pwd)"

# Create data directory for SQLite (Azure ephemeral storage)
mkdir -p /home/site/wwwroot/data

# Run migrations
echo "==> Running Alembic migrations..."
python -m alembic upgrade head

# Start Gunicorn with Uvicorn workers (Azure App Service standard)
echo "==> Starting server..."
exec gunicorn src.main:app \
  --workers 2 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120 \
  --keep-alive 5 \
  --log-level info
