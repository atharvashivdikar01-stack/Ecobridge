<<<<<<< Updated upstream
# Repository Guidelines

## Project Structure & Module Organization
This repository is currently empty, so contributors should keep the initial layout simple and predictable. Place application code in `src/`, tests in `tests/`, static assets in `assets/`, and project documentation in `docs/`. Keep root-level files limited to repository metadata and tool configuration such as `README.md`, `.gitignore`, and formatter or linter configs.

Example layout:
```text
src/
tests/
assets/
docs/
```

## Build, Test, and Development Commands
No build system is configured yet. When introducing one, document the standard local workflow in `README.md` and keep commands consistent across contributors.

Recommended baseline commands:
- `npm install` or equivalent dependency restore command
- `npm run dev` for local development
- `npm test` for the default test suite
- `npm run lint` and `npm run format` for code quality

Only add commands that are wired into the repository and safe for other contributors to run.

## Coding Style & Naming Conventions
Use 4 spaces for indentation unless the chosen language ecosystem strongly prefers otherwise. Name files and directories consistently: `kebab-case` for frontend or config files, `snake_case` for Python modules, and `PascalCase` for class names. Keep functions small, prefer descriptive identifiers, and avoid adding multiple competing patterns in the first commit.

Adopt an automated formatter and linter as soon as the primary stack is chosen.

## Testing Guidelines
Put tests under `tests/` and mirror the structure of `src/`. Use names that make scope obvious, such as `tests/api/test_health.py` or `src/components/button.test.ts`. Add at least one automated test for each new feature or bug fix, and make sure the default test command runs cleanly before opening a PR.

## Commit & Pull Request Guidelines
Git history is not available in this workspace, so no repository-specific commit convention could be inferred. Use short, imperative commit messages such as `Add initial API scaffold` or `Fix login validation`.

For pull requests, include:
- a clear summary of the change
- linked issue or task ID when applicable
- test evidence
- screenshots for UI changes

## Security & Configuration Tips
Do not commit secrets, local environment files, or generated credentials. Keep sensitive values in ignored local config files such as `.env` and document required variables in `README.md`.
=======
# AGENTS.md — Contributor & AI Agent Guidelines for ECOBRIDGE

Welcome to the **ECOBRIDGE** repository. This document establishes technical invariants, architecture standards, directory responsibilities, and operating procedures for both human engineers and AI coding agents working on this codebase.

---

## 1. Project Mission & Invariants

ECOBRIDGE bridges the gap between informal e-waste collectors (waste pickers, scrap aggregators, *kabadiwalas*) and certified recyclers.

Whenever modifying or adding code, preserve these **non-negotiable core invariants**:

1. **Offline-First Resilience:**
   - The collector mobile app (`apps/collector-mobile`) must remain fully operational without internet.
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
├── apps/
│   ├── collector-mobile/    # React Native / Expo offline client for collectors
│   ├── recycler-portal/     # Next.js web application for certified recyclers
│   ├── admin-dashboard/     # Next.js platform admin & regulator portal
│   └── api-server/          # NestJS / Fastify core backend and microservices
├── packages/
│   ├── api-contracts/       # Shared TypeScript types, DTOs, and Zod schemas
│   ├── database/            # PostgreSQL schemas, migrations, and ORM clients
│   ├── sync-engine/         # Delta sync protocol, CRDTs, and offline queue logic
│   ├── ai-core/             # Vision model definitions, hazard dictionaries, pricing math
│   ├── crypto-traceability/ # SHA-256 chain-of-custody, QR generators, digital signatures
│   ├── ui/                  # Shared React component library & Tailwind tokens
│   ├── i18n/                # Multilingual translations and voice prompt dictionaries
│   ├── tsconfig/            # Shared TypeScript configurations
│   └── eslint-config/       # Unified ESLint & formatting rules
├── infra/
│   ├── docker/              # Multi-stage Dockerfiles and local docker-compose
│   ├── k8s/                 # Kubernetes manifests and Helm charts
│   └── terraform/           # Infrastructure as Code
└── scripts/                 # Development, migration, and AI pipeline scripts
```

### Dependency Rules:
- **`apps/*`** may depend on any **`packages/*`**, but **never** on another app.
- **`packages/*`** should be as leaf-oriented as possible. For instance, `packages/api-contracts` has zero internal workspace dependencies.
- Use `workspace:*` in `package.json` for internal package references.

---

## 3. Technology Stack & Tooling

- **Workspace Manager:** `pnpm` (version >= 9) with `Turborepo` (version >= 2).
- **Backend Runtime:** Node.js (LTS >= 18) with TypeScript (strict mode enabled).
- **Mobile Client:** React Native with Expo bare workflow + SQLite / WatermelonDB.
- **Web Applications:** Next.js (App Router), Tailwind CSS, TanStack Query.
- **Databases:** PostgreSQL 16 (with PostGIS extension) and Redis for caching/queues.
- **Validation:** Zod schemas for all network boundary inputs.

---

## 4. Coding & Architecture Conventions

### TypeScript
- All code must be strictly typed. **`any` is strictly prohibited.** Use `unknown` with Zod parsing or type guards.
- Prefer explicit return types on exported functions and API route handlers.
- Barrel exports (`index.ts`) must only expose public APIs of each package.

### Error Handling & API Responses
- All backend REST endpoints must return structured responses adhering to the shared `ApiResponse<T>` contract:
  ```typescript
  export interface ApiResponse<T> {
    success: boolean;
    data?: T;
    error?: {
      code: string;
      message: string;
      details?: unknown;
    };
    timestamp: string;
  }
  ```
- Always pass an `Idempotency-Key` header on mutating offline-sync requests.

### Database Changes
- Never modify existing migration files that have been applied. Always generate a new forward migration.
- Use soft-deletes or append-only event logs for financial records, lot updates, and custody events.

---

## 5. Agent Workflow Guidelines

When executing a task in this repository:
1. **Understand boundaries:** Determine whether the change belongs in an app (`apps/`) or a shared package (`packages/`).
2. **Contract first:** If updating an API or data model, update `packages/api-contracts` first, then consumer apps.
3. **Run builds & lint:** Always run `pnpm turbo run lint` and `pnpm turbo run test` before submitting changes.
4. **Preserve comments & docs:** Keep existing architecture notes and inline docstrings accurate and clean.
>>>>>>> Stashed changes
