#!/bin/bash
set -e

echo "==> EcoBridge Root Startup Script"
if [ -d "/home/site/wwwroot/backend" ]; then
    cd /home/site/wwwroot/backend
elif [ -d "backend" ]; then
    cd backend
fi

bash startup.sh
