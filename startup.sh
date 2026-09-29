#!/bin/bash
set -e

echo "==> EcoBridge Root Startup Script"
echo "==> Working directory: $(pwd)"

PORT="${PORT:-8000}"
mkdir -p /home/site/wwwroot/data || mkdir -p data || true

if [ -f "/antenv/bin/activate" ]; then
    echo "==> Activating /antenv"
    source /antenv/bin/activate
fi

if [ -d "/home/site/wwwroot/backend" ]; then
    cd /home/site/wwwroot/backend
elif [ -d "backend" ]; then
    cd backend
fi

# Run migrations if alembic is present
if command -v alembic >/dev/null 2>&1; then
    echo "==> Running Alembic migrations..."
    alembic upgrade head || true
fi

echo "==> Starting server on port $PORT..."
if command -v gunicorn >/dev/null 2>&1; then
    echo "==> Running with Gunicorn..."
    exec gunicorn src.main:app \
      --workers 2 \
      --worker-class uvicorn.workers.UvicornWorker \
      --bind 0.0.0.0:$PORT \
      --timeout 120 \
      --keep-alive 5 \
      --log-level info
else
    echo "==> Running with Uvicorn..."
    exec python -m uvicorn src.main:app --host 0.0.0.0 --port $PORT
fi
