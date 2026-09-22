# Copilot instructions — Kabadiwala Connect / ECOBRIDGE

Project: offline-first mobile app (React Native / Expo) + FastAPI backend + Next.js recycler web dashboard
for informal e-waste collectors in India. Full context, data model and rules are in CONTEXT.md at the repo root.
Read it before suggesting schema, API or architecture changes.

## Who is writing this code
- The team are beginners (basic Python, TypeScript, Android, web). Prefer simple, readable code over clever code.
- Add short comments for anything non-obvious, and summarise in one line what the code does.

## Stack (do not change without asking)
- Mobile: React Native, Expo, SQLite / WatermelonDB, TensorFlow Lite
- Backend: Python, FastAPI, SQLAlchemy Async, Pydantic, JSON REST under /api/v1
- Web Portals: Next.js (App Router), React, Tailwind CSS
- Monorepo: pnpm workspaces, Turborepo
- Shared packages: @ecobridge/api-contracts, @ecobridge/database, @ecobridge/ui, @ecobridge/i18n
- Do not introduce new frameworks or libraries unless asked.

## Rules
- Offline-first: write to local SQLite first, sync later with an outbox queue.
  Lot IDs are UUIDs created on the device. Server endpoints must be idempotent.
- No hardcoded UI text: use @ecobridge/i18n translation tokens for all user-facing strings.
  Support English, Marathi (mr), and Hindi (hi) at minimum.
- Timestamps are UTC ISO-8601, weights in kg, money in INR.
- Keep personal data minimal. Never invent prices, recycler names or registration numbers.
  Mark test data as synthetic.
- Naming: Python snake_case, TypeScript camelCase/PascalCase, file names kebab-case.
- Keep the APK small: avoid heavy dependencies.
- TypeScript: strict mode, no `any` — use `unknown` with Zod or type guards.

## When unsure
- Ask a clarifying question or list your assumptions instead of guessing.
