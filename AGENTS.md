# AGENTS.md — Contributor & AI Agent Guidelines for ECOBRIDGE

Welcome to the **ECOBRIDGE** repository. This document establishes technical invariants, architecture standards, directory responsibilities, and operating procedures for both human engineers and AI coding agents working on this codebase.

---

## 1. Project Mission & Invariants

ECOBRIDGE bridges the gap between informal e-waste collectors (waste pickers, scrap aggregators, *kabadiwalas*) and certified recyclers.

Whenever modifying or adding code, preserve these **non-negotiable core invariants**:

1. **Offline-First Resilience:**
   - The collector mobile app (`collector_app`) must remain fully operational without internet.
   - All collection records, image references, and lot manifests must persist to the local store (SQLite / WatermelonDB) immediately.
   - Network interactions must always go through the background sync queue (`packages/sync-engine`).

2. **Strict Type Safety & Contract Sharing:**
   - Never duplicate interfaces, DTOs, or payload schemas between client and server.
   - All shared data models, API payloads, and validation schemas belong in `packages/api-contracts` (using TypeScript and Zod).

3. **Deterministic Traceability & Auditability:**
   - The chain of custody (`packages/crypto-traceability`) is tamper-evident. Every batch transition requires previous-hash verification, actor ID, and cryptographic timestamping.
   - Never allow batch status updates without logging a corresponding custody event.

4. **Safety & Hazard Warnings First:**
   - AI material recognition (`packages/ai-core`) must prioritize identifying hazardous conditions (swollen batteries, broken CRT glass, burnt PCBs) and immediately render safety/PPE alerts before price estimates.

5. **Accessibility & Vernacular Support:**
   - All collector-facing UI text, labels, and audio prompts must reference translation tokens in `packages/i18n`. Hardcoded English strings in mobile views are prohibited.

---

## 2. Monorepo Organization & Directory Ownership

```text
ecobridge/
├── backend/                     # FastAPI async backend and microservices
│   ├── src/
│   │   ├── api/v1/endpoints/    # Route handlers
│   │   ├── services/            # Business logic
│   │   ├── models/              # SQLAlchemy ORM models
│   │   ├── schemas/             # Pydantic request/response schemas
│   │   └── core/                # Config, database, security, exceptions
│   └── tests/                   # pytest async test suite
├── recycler_portal/             # Next.js web app for certified recyclers
├── admin_dashboard/             # Next.js platform admin & regulator portal
├── collector_app/               # React Native / Expo offline client
├── packages/
│   ├── api-contracts/           # Shared TypeScript types, DTOs, and Zod schemas
│   ├── database/                # PostgreSQL schemas, migrations, and ORM clients
│   ├── sync-engine/             # Delta sync protocol, CRDTs, and offline queue logic
│   ├── ai-core/                 # Vision model definitions, hazard dictionaries, pricing math
│   ├── crypto-traceability/     # SHA-256 chain-of-custody, QR generators, digital signatures
│   ├── ui/                      # Shared React component library & Tailwind tokens
│   ├── i18n/                    # Multilingual translations and voice prompt dictionaries
│   ├── tsconfig/                # Shared TypeScript configurations
│   └── eslint-config/           # Unified ESLint & formatting rules
├── infra/
│   ├── docker/                  # Multi-stage Dockerfiles and local docker-compose
│   ├── k8s/                     # Kubernetes manifests and Helm charts
│   └── terraform/               # Infrastructure as Code
├── docs/                        # Project documentation
├── datasets/                    # AI/ML training datasets
├── tests/                       # Integration tests
└── scripts/                     # Development, migration, and AI pipeline scripts
```

### Dependency Rules:
- **`recycler_portal/`**, **`admin_dashboard/`**, **`collector_app/`** may depend on any **`packages/*`**, but **never** on each other.
- **`packages/*`** should be as leaf-oriented as possible. `packages/api-contracts` has zero internal workspace dependencies.
- Use `workspace:*` in `package.json` for internal package references.

---

## 3. Technology Stack & Tooling

- **Workspace Manager:** `pnpm` (version >= 9) with `Turborepo` (version >= 2).
- **Backend Runtime:** Python 3.11+ with FastAPI, SQLAlchemy Async, Pydantic v2.
- **Mobile Client:** React Native with Expo + SQLite / WatermelonDB.
- **Web Applications:** Next.js (App Router), Tailwind CSS, TanStack Query.
- **Databases:** PostgreSQL 16 (with PostGIS extension) and Redis for caching/queues.
- **Validation:** Pydantic schemas (backend), Zod schemas (frontend) for all network boundary inputs.

---

## 4. Coding & Architecture Conventions

### Python / FastAPI
- PEP 8, snake_case. One router per feature domain.
- Async endpoints with `AsyncSession`. Pydantic schemas for all request/response payloads.
- Config from environment (`.env`). Never commit secrets or API keys.

### TypeScript
- All code must be strictly typed. **`any` is strictly prohibited.** Use `unknown` with Zod parsing or type guards.
- Prefer explicit return types on exported functions and API route handlers.
- Barrel exports (`index.ts`) must only expose public APIs of each package.

### Error Handling & API Responses
- All backend REST endpoints must return structured responses adhering to the shared `ApiResponse<T>` contract:
  ```python
  class ApiResponse(BaseModel, Generic[T]):
      success: bool
      data: Optional[T] = None
      error: Optional[ErrorDetail] = None
      timestamp: str
  ```
- Always pass an `Idempotency-Key` header on mutating offline-sync requests.

### Database Changes
- Never modify existing migration files that have been applied. Always generate a new forward migration.
- Use soft-deletes or append-only event logs for financial records, lot updates, and custody events.

---

## 5. Agent Workflow Guidelines

When executing a task in this repository:
1. **Understand boundaries:** Determine whether the change belongs in an app or a shared package (`packages/`).
2. **Contract first:** If updating an API or data model, update `packages/api-contracts` first, then consumer apps.
3. **Run builds & lint:** Always verify code compiles and lints before submitting changes.
4. **Preserve comments & docs:** Keep existing architecture notes and inline docstrings accurate and clean.
