# ECOBRIDGE — Developer Guide & Setup

Welcome to the **ECOBRIDGE** development guide. This document outlines how to set up your local development environment, run services, test features, and contribute effectively.

---

## 1. Prerequisites

Ensure the following tools are installed on your machine:
- **Node.js**: `v18.0.0` or higher (LTS recommended)
- **pnpm**: `9.15.0` (the version declared by `packageManager`)
- **Git**: For source control
- **Python**: `3.11` or higher
- **Docker & Docker Compose**: Optional; use only when working on the local
  infrastructure configuration

---

## 2. Initial Setup

### Step 1: Run the Automated Setup Script
```bash
git clone https://github.com/atharvashivdikar01-stack/Ecobridge.git
cd Ecobridge

# Optional shell helper for checking local prerequisites
./scripts/dev-setup.sh
```

### Step 2: Install Workspace Dependencies
```bash
pnpm install
```

Copy `backend/.env.example` to `backend/.env` and
`recycler_portal/.env.example` to `recycler_portal/.env.local`, then replace
placeholders with local-only values.

---

## 3. Everyday Development Workflows

### Running Applications
The declared pnpm workspace currently includes `recycler_portal` and
`packages/*`:

```bash
pnpm --filter @ecobridge/recycler-portal dev
```

Run the FastAPI backend separately:

```bash
uvicorn src.main:app --reload --port 8000 --app-dir backend
```

### Building & Checking Code
```bash
# Typecheck and build the active portal
pnpm --dir recycler_portal exec tsc --noEmit
pnpm build

# Lint the active portal
pnpm lint

# Run backend tests (Windows PowerShell)
$env:PYTHONPATH = "backend"; python -m pytest backend/tests -q
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

Database schema and migrations reside in `packages/database/`; run these only
when working on that package:

```bash
# Generate/apply a local database migration
pnpm --filter @ecobridge/database db:migrate

# Seed local database with mock collectors, recyclers, and scrap prices
pnpm --filter @ecobridge/database db:seed

# Inspect the database using Prisma Studio
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
