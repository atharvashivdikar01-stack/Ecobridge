#!/usr/bin/env bash
set -euo pipefail

echo "=========================================="
echo "  🌿 ECOBRIDGE Developer Setup Script    "
echo "=========================================="

# Check for Git
if ! command -v git &> /dev/null; then
  echo "❌ Error: git is not installed."
  exit 1
fi
echo "✅ Git is installed."

# Check for Node.js
if ! command -v node &> /dev/null; then
  echo "⚠️  Node.js is not found in standard PATH."
  echo "   Please install Node.js (>= v18.0.0) via NVM, FNM, or Homebrew (brew install node)."
else
  NODE_VER=$(node -v)
  echo "✅ Node.js is installed ($NODE_VER)."
fi

# Check for pnpm
if ! command -v pnpm &> /dev/null; then
  echo "⚠️  pnpm is not found in standard PATH."
  echo "   You can enable pnpm via: corepack enable && corepack prepare pnpm@latest --activate"
else
  PNPM_VER=$(pnpm -v)
  echo "✅ pnpm is installed ($PNPM_VER)."
fi

# Check for Docker
if ! command -v docker &> /dev/null; then
  echo "⚠️  Docker is not installed or not running. Please install Docker Desktop for database containers."
else
  echo "✅ Docker is installed."
fi

# Create default local .env if missing
if [ ! -f .env ]; then
  echo "📝 Creating initial .env file..."
  cat << 'EOF' > .env
NODE_ENV=development
PORT=3000
DATABASE_URL=postgresql://ecobridge:ecobridge_dev_password@localhost:5432/ecobridge_dev?schema=public
REDIS_URL=redis://localhost:6379
MINIO_ENDPOINT=localhost
MINIO_PORT=9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin_dev
EOF
  echo "✅ Created .env"
fi

echo "=========================================="
echo "  Setup verification complete! 🎉         "
echo "  Next steps:                             "
echo "    1. docker compose -f infra/docker/docker-compose.yml up -d"
echo "    2. pnpm install                       "
echo "    3. pnpm dev                           "
echo "=========================================="
