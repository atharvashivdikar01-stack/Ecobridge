# EcoBridge

EcoBridge connects informal e-waste collectors with recycling facilities through
transparent collection records, pricing, verification, handover, and settlement
workflows.

## Current implementation

- **Backend:** FastAPI, SQLAlchemy async, PostgreSQL in production, SQLite for tests.
- **Recycler portal:** Next.js 14 and React 18.
- **Collector app:** Expo/React Native package placeholder and implementation guide.
- **Shared packages:** API contracts, AI classification types, offline sync types,
  translations, traceability hashing, UI, and database scaffolding.

The current repository is a working foundation. Payment gateways, production
SMS/OTP delivery, live market feeds, and a complete collector mobile UI still
require deployment-specific integration.

## Repository layout

```text
backend/          FastAPI application, models, services, and tests
recycler_portal/  Next.js recycler operations portal
collector_app/    Expo package metadata and Android implementation guide
packages/         Shared TypeScript packages
docs/             Development and Android setup documentation
scripts/          Local setup helpers
infra/            Deployment notes
```

## Prerequisites

- Python 3.11+
- Node.js 18+
- pnpm 9.15.0 (the version declared by `packageManager`)
- PostgreSQL for production; SQLite is used by the automated tests

## Backend setup

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

Set `DATABASE_URL` and `SECRET_KEY` through environment variables. Never commit
`.env` files or real credentials.

Run the API:

```bash
uvicorn src.main:app --reload --port 8000
```

Run the backend tests:

```bash
set PYTHONPATH=backend
python -m pytest backend/tests -q
```

## Recycler portal

```bash
pnpm install
pnpm --filter @ecobridge/recycler-portal dev
```

The portal runs on `http://localhost:3001` and proxies `/api/v1` to the backend
at `http://127.0.0.1:8000`. Override the API URL with
`NEXT_PUBLIC_API_URL` when required.

Production checks:

```bash
pnpm build
pnpm --filter @ecobridge/recycler-portal start
```

## Android collector app

The partner folder did not contain a complete Android application. The
authoritative implementation plan is [`docs/ANDROID_APP.md`](docs/ANDROID_APP.md).
It covers Expo setup, emulator/device networking, authentication, camera and
location permissions, offline queueing, synchronization, and release testing.

## Security and privacy

Use environment variables for database URLs, JWT secrets, storage credentials,
and external API keys. Demo login is for local demonstrations only. Review
privacy, consent, data retention, and regulatory requirements before production
deployment.

See [`CONTRIBUTING.md`](CONTRIBUTING.md), [`SECURITY.md`](SECURITY.md), and
[`docs/RELEASE.md`](docs/RELEASE.md) for contribution, vulnerability reporting,
and release validation guidance.

## License

MIT. See [LICENSE](LICENSE).
