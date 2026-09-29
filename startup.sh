#!/bin/bash
set -e

echo "==> EcoBridge Root Startup Script"
echo "==> Working directory: $(pwd)"

if [ -f "/antenv/bin/activate" ]; then
    source /antenv/bin/activate
fi

if [ -d "/home/site/wwwroot/backend" ]; then
    cd /home/site/wwwroot/backend
elif [ -d "backend" ]; then
    cd backend
fi

bash startup.sh
