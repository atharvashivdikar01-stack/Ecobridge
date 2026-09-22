# ECOBRIDGE — Developer Guide & Setup

Welcome to the **ECOBRIDGE** development guide. This document outlines how to set up your local development environment, run services, test features, and contribute effectively.

---

## 1. Prerequisites

Ensure the following tools are installed on your machine:
- **Node.js**: `v18.0.0` or higher (LTS recommended)
- **pnpm**: `v9.0.0` or higher (`corepack enable && corepack prepare pnpm@latest --activate` or `npm i -g pnpm`)
- **Docker & Docker Compose**: For local PostgreSQL, Redis, and MinIO instances
- **Git**: For source control
- *(Optional for AI model training)*: **Python 3.10+** with `virtualenv`

---

## 2. Initial Setup

### Step 1: Run the Automated Setup Script
```bash
git clone https://github.com/atharvashivdikar01-stack/Ecobridge.git
cd Ecobridge

# Run the automated onboarding script
chmod +x scripts/dev-setup.sh
./scripts/dev-setup.sh
```

### Step 2: Install Workspace Dependencies
```bash
pnpm install
```

### Step 3: Launch Local Infrastructure
Start the supporting containerized services:
```bash
docker compose -f infra/docker/docker-compose.yml up -d
```
This boots:
- **PostgreSQL 16 + PostGIS**: `localhost:5432` (User: `ecobridge`, DB: `ecobridge_dev`)
- **Redis 7**: `localhost:6379`
- **MinIO S3 Emulator**: `localhost:9000` (Console: `localhost:9001`)

---

## 3. Everyday Development Workflows

### Running Applications
Turborepo orchestrates commands across all workspaces:

```bash
# Start all applications in dev mode concurrently
pnpm dev

# Target a specific app
pnpm --filter @ecobridge/api-server dev
pnpm --filter @ecobridge/recycler-portal dev
pnpm --filter @ecobridge/admin-dashboard dev
pnpm --filter @ecobridge/collector-mobile start
```

### Building & Checking Code
```bash
# Typecheck and build all packages
pnpm build

# Run linting across all workspaces
pnpm lint

# Run automated tests
pnpm test
```

---

## 4. Package Dependency Structure

Our monorepo uses `pnpm` workspaces. To consume a shared internal package in an app:

In `apps/api-server/package.json`:
```json
{
  "dependencies": {
    "@ecobridge/api-contracts": "workspace:*",
    "@ecobridge/database": "workspace:*",
    "@ecobridge/sync-engine": "workspace:*"
  }
}
```

### Internal Package Summary:
- `@ecobridge/api-contracts`: DTOs, interfaces, and Zod schemas shared across frontend & backend.
- `@ecobridge/database`: ORM schemas, migration runners, and database client.
- `@ecobridge/sync-engine`: Offline queue logic and reconciliation algorithms.
- `@ecobridge/ai-core`: Quantized edge models, hazard dictionaries, and pricing math.
- `@ecobridge/crypto-traceability`: SHA-256 chain of custody and digital signatures.
- `@ecobridge/ui`: Shared React components and Tailwind styling tokens.
- `@ecobridge/i18n`: Multilingual translations and voice prompt dictionaries.

---

## 5. Working with the Database

Database migrations and models reside in `packages/database/`:

```bash
# Generate database migration
pnpm --filter @ecobridge/database db:migrate:dev

# Seed local database with mock collectors, recyclers, and scrap prices
pnpm --filter @ecobridge/database db:seed

# Inspect database using Prisma/Drizzle Studio
pnpm --filter @ecobridge/database db:studio
```

---

## 6. Testing & Quality Standards

- **Unit Testing**: Place unit tests adjacent to source files (`*.test.ts` or `*.spec.ts`).
- **Offline Sync Testing**: Always test mutations against offline state machines before submitting PRs.
- **Contract Verification**: Never make breaking changes to `packages/api-contracts` without updating all consuming applications.

---

## 7. Git & Pull Request Guidelines

1. Create a feature branch from `main`:
   ```bash
   git checkout -b feature/collector-offline-queue
   ```
2. Ensure linting and tests pass before committing:
   ```bash
   pnpm lint && pnpm test
   ```
3. Submit a PR with a clear description referencing the architectural module being addressed.
