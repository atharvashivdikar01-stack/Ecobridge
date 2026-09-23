# EcoBridge (Kabadiwala Connect) — Jury Prep Master Document
**SIH 2026, Problem Statement 26229 — Ministry of Mines / JNARDDC**

This document is based on a direct code analysis of your repo, not just the README. It flags what is real, what is a stub, and what is aspirational — so you never get caught off guard.

---

## 1. What the project actually is

A vernacular (Marathi + Hindi), low-literacy, **offline-first Android app** for informal e-waste collectors (kabadiwalas) to:
1. Photograph and log a "lot" of e-waste
2. Get an AI-assisted category suggestion + fair price estimate
3. Find nearby **authorized** recyclers
4. Complete a traceable handover
5. Track a simple cash-first earnings ledger

Plus a **web portal for recyclers** to accept lots, confirm handovers, and settle payment.

**Legal positioning (memorize this):** the handover record is a *verifiable receipt / traceability aid*, **not** a legal manifest. Never claim regulatory/EPR compliance in the pitch — this is explicitly called out in your own `CONTEXT.md`.

---

## 2. The single most important thing to know before you present

Your repo contains **two parallel implementations** of almost everything, from two merge histories that were never fully reconciled:

| Layer | Real / active (wired into the build) | Leftover / not wired in |
|---|---|---|
| Backend | `backend/` — Python FastAPI, async SQLAlchemy | `apps/api-server/` — package.json claims Node.js + Fastify + tsup, but the folder actually contains **Python** FastAPI files copy-pasted in. It cannot run as configured. |
| Recycler frontend | `recycler_portal/` — real Next.js 14 app, working pages (dashboard, materials, handover, payment, ledger) | `apps/recycler-portal/` — a static `server.js` + plain HTML/CSS/JS stub whose `build` script literally just prints `"Build ready"` and whose `test` script prints `"Tests passing"` without testing anything |
| Workspace config | `pnpm-workspace.yaml` only includes `recycler_portal`, `collector_app`, and `packages/*` | The entire `apps/` folder is **not part of the pnpm workspace** — it's dead weight sitting in the repo |

**Why this happened:** `IMPLEMENTATION_PLAN.md` in the repo documents that two contributors' codebases were merged, and cleanup wasn't finished (duplicate READMEs, duplicate package.json files, a `backend/app.py` Flask prototype scheduled for conversion, etc.).

**What to do about it:** Be upfront if asked — "we merged two early prototypes, `backend/` and `recycler_portal/` are the ones we actually run and demo; `apps/` is leftover scaffolding from that merge we haven't deleted yet." Do **not** demo anything from `apps/`. Do not claim Node.js/Fastify/PostGIS/Redis/MinIO/Kubernetes/Terraform — these appear in `docs/ARCHITECTURE.md` as an aspirational architecture doc but are **not implemented** anywhere in actual code.

---

## 3. Technologies actually used (say this, and only this, with confidence)

### Backend — `backend/`
- **Python 3.11+, FastAPI** (async web framework)
- **SQLAlchemy 2.x (async)** as the ORM
- **PostgreSQL** in production, **SQLite** for automated tests (via `aiosqlite`)
- **asyncpg** as the async Postgres driver
- **Alembic** for database migrations
- **Pydantic v2 / pydantic-settings** for schema validation and config
- **python-jose** for JWT access/refresh tokens
- **pytest + pytest-asyncio** for backend tests (5 test files: config, lots, recycler portal, collector auth/profile, matching, pricing, health, error handling)
- REST JSON API under `/api/v1`, versioned router pattern, one router per feature (auth, collectors, lots, matching, pricing, recyclers, recycler_portal, health)

### Recycler Portal — `recycler_portal/`
- **Next.js 14** (App Router), **React 18**
- **Tailwind CSS 3** for styling
- **TypeScript**
- Pages: login, dashboard (overview), materials list + detail, handover, payment, ledger
- Talks to the backend via a typed `app/lib/api.ts` client, proxying `/api/v1` to `http://127.0.0.1:8000`
- Runs on `localhost:3001`

### Collector App — `collector_app/`
- **Expo / React Native** — currently a **package scaffold + implementation guide only** (`docs/ANDROID_APP.md`), not a built app. Be honest about this: it's your documented plan, not working code yet.
- Planned local storage: SQLite / WatermelonDB (offline-first, source of truth on-device)
- Planned on-device classifier: TensorFlow Lite, ~8 material classes
- Fallback plan if native build stalls: a PWA (HTML/JS + service worker + IndexedDB) wrapped as an APK

### Shared TypeScript packages — `packages/*` (pnpm workspace + Turborepo)
Be careful here — most of these are currently **type-definition stubs (3–12 lines each)**, not working implementations. It's honest and fine to call them "scaffolded shared contracts we're building out," but don't claim they contain real logic today:
- `api-contracts` — shared TS types (e.g. `LotStatus`)
- `ai-core` — type for a `MaterialClassification` result shape only
- `crypto-traceability` — **this one is real**: a working `hashCustodyEvent()` function using Node's `crypto` SHA-256, chaining `previousHash + payload` — a genuine hash-chain building block
- `sync-engine` — type for a `SyncRecord` state shape only
- `ui`, `i18n` (has real `en.json`, `hi.json`, `mr.json` locale files), `tsconfig`, `eslint-config` — shared config/tooling packages

### Monorepo tooling
- **pnpm workspaces** + **Turborepo** for orchestrating build/dev/lint/test across packages

### Datasets (this is a genuine strength — lean on it)
A dedicated `datasets/` directory with a `DATASET_REGISTER.md` that documents **provenance and honesty tags** for every dataset:
- Operational: materials, prices, recyclers, transactions, traceability, collectors, audio prompts (CSV + JSON + SQL seed)
- AI/ML: CPCB recycler registry, 12–15 month historical price trends, a field scrap photo manifest, a data-flywheel of confirmed labels, and a small YOLO-format vision benchmark (8 classes: CRT, LCD/LED panel, PCB, cables, batteries, motors/magnets, mixed plastics, other e-waste)
- Some genuine field images are sourced from the **GIZ E-Waste Database (Hugging Face, CC-BY-4.0)** with proper attribution — a good, defensible detail if asked about data ethics
- **Be accurate:** the vision dataset currently has only ~5 training + 2 validation images per class (40–56 images total) — a seed/demo set for the pipeline, not a trained production model. **No `.pt` or `.tflite` weight file exists in the repo.** If asked "is your AI model trained?", the honest answer is: "We've built and validated the data pipeline and labeling format; the classifier itself is the next milestone, not yet trained on production data."

---

## 4. What's real vs. stub inside the backend (know this cold)

| Feature | Status | Detail |
|---|---|---|
| Auth (OTP + JWT) | **Real logic, mock OTP delivery** | `otp_service.py` always issues/accepts the hardcoded code `123456` — there's no real SMS gateway yet. This is intentional for demos but you must say so if asked "do collectors get a real SMS?" |
| Lot creation | **Real** | `lot_service.py` genuinely creates a lot, looks up live material price bands, computes weight × price subtotal per item, stores photo hashes (SHA-256), and writes a custody event with a hash chain (`previous_event_hash` / `current_event_hash`) |
| Demo login | **Real, and intentional** | A dedicated `/auth/demo-login` endpoint lets you instantly log in as a Verified Recycler, an Unverified Recycler, or a Collector — built specifically for live competition demos |
| Price intelligence engine | **Stub** | `price_intelligence_service.py` currently returns empty/zero placeholder data. The "weight × recycler rate × condition factor" formula described in `CONTEXT.md` is the intended design, not yet the executing code |
| Recycler-lot matching | **Stub** | `matching_service.py` returns an empty match list — the ranking-by-rate/distance/pickup-availability logic is designed but not implemented |
| Recycler service (authorizations, service areas, accepted materials) | **Mostly stubs** | Registering a recycler company and adding a facility works; authorization tracking, accepted-materials config, and service-area management currently return empty placeholders |
| Collector profile/stats | **Real but thin** | Reads real fields off the DB profile (trust score, total lots, total weight) |
| Recycler portal UI pages | **Real** | Materials (406 lines) and Payment (429 lines) pages are substantial, with real typed data models — this is genuinely built, not a mockup |

**One-line summary you can say out loud:** *"Authentication, lot creation with pricing and a hash-chained custody trail, and the recycler portal UI are working end-to-end. Live pricing intelligence, automated recycler matching, and the on-device AI classifier are designed and data-modeled, but still stubs — that's our next sprint."*

---

## 5. Likely jury questions, with strong answers

### Product / problem framing

**Q1: Why should an informal collector trust or use this app at all?**
A: The MVP requires zero personal data (name/phone are optional), works fully offline, defaults to cash payment, and gives the collector something they don't have today — a fair, transparent price estimate and a receipt they can point to if a recycler tries to lowball them. Trust is earned through low friction, not mandates.

**Q2: How is this different from the collector just asking recyclers directly?**
A: Today a collector has no way to compare rates across recyclers, no proof of what was handed over, and no record of pending dues. EcoBridge adds: (1) a live-ish price board so they know a fair range before they even reach a recycler, (2) a recycler ranking so they're steered toward authorized buyers, (3) a handover record with photos, weight, GPS and a short code both sides can verify, and (4) an earnings ledger so nothing gets forgotten.

**Q3: What exactly does "traceability" mean here — is this a legal manifest?**
A: No — and we're careful never to claim that. It's a verifiable receipt: a SHA-256 hash chain of custody events (creation → handover → confirmation), timestamps, GPS, and photos. It's evidence a dispute can be resolved against, not a regulatory Form 2/3 filing. Regulatory-grade EPR manifests are a different, harder problem we've deliberately scoped out of the MVP.

**Q4: Field research — how many real collectors/aggregators have you actually spoken to?**
A: [Fill in with your real number — the problem statement explicitly requires "at least 2 real collectors/aggregators." Have concrete names/photos/quotes ready if you have them; if you don't have this yet, be honest and describe your plan and timeline rather than inventing numbers.]

**Q5: What's your unit economics / business model?**
A: [Fill in — problem statement explicitly asks for this. A reasonable framing: a small transaction fee or subscription on the recycler side once they get verified volume/traceability/compliance-adjacent reporting value from the platform; the collector side stays free to keep adoption frictionless.]

### Technical depth

**Q6: Walk me through what happens, technically, from photo to payment.**
A: On-device: photo → (planned) TFLite classifier suggests a category, collector confirms/corrects from an icon grid → weight entered → the app looks up the cached price board and shows an instant estimate → everything is written to local SQLite first (the device is the source of truth until synced). When connectivity returns, an outbox queue does an idempotent upsert to the backend (`POST /api/v1/sync`) keyed by a device-generated UUIDv4 lot ID, so re-sending the same lot never duplicates it. On the backend, `lot_service.create_lot()` resolves the current price band for each material, computes `weight × price` per item, sums up the lot value, hashes each photo (SHA-256), and writes a `CustodyEvent` with a chained hash. The recycler sees it in the Next.js portal, confirms weight at the weighbridge, and a payment/ledger entry is recorded (cash by default, UPI optional).

**Q7: Why FastAPI + Next.js instead of one full JS or one full Python stack?**
A: We wanted async, typed request/response validation and easy SQLAlchemy access on the backend (FastAPI is strong for this), while the recycler-facing portal benefits from React's component ecosystem, Tailwind for fast UI iteration, and Next.js's App Router for simple page-based routing. A shared `api-contracts` package (currently early-stage) is intended to keep both sides' types in sync as it matures.

**Q8: How do you resolve sync conflicts between the phone and the server?**
A: A field-level rule, not "last write wins" globally: physical collection facts (photos, initial weight, items) are **client-wins**, because the collector recorded ground truth first. Lot status/approval and price locks are **server-wins**, because only the backend state machine or the recycler can authoritatively change those.

**Q9: Is your AI/ML classifier actually trained and running?**
A: Be honest per Section 4 above: the data pipeline, YOLO-format labeling, and an 8-class taxonomy are built and validated on a small seed dataset (including real field images from the GIZ E-Waste Database under CC-BY-4.0). We have not yet trained and shipped a `.tflite` weight file — that's explicitly the next milestone. In the meantime, low-confidence or missing classification falls back to the collector picking from an icon grid, and those confirmed picks become new training data (a data flywheel we've already modeled in `confirmed_labels.csv`).

**Q10: What happens with zero or patchy internet — is this a real offline app or a "requires internet, fails ungracefully" app?**
A: Offline-first is a written architectural rule (`AGENTS.md`, `CONTEXT.md`), not an afterthought: local SQLite/WatermelonDB write-first, an outbox sync queue, and a cached price board with a visible "last updated" timestamp so the collector always knows if they're looking at stale prices. The mobile app itself isn't fully built yet (see Q13) — the offline design is implemented in principle at the data-model and API level (idempotent sync endpoint, UUID-based lot IDs) and is the guide for the Android build.

**Q11: How do you prevent price manipulation or a recycler colluding to underpay?**
A: The price board is meant to be a mix of field survey data, recycler-submitted rates, and (labeled) synthetic data — never blended without a `source_type` tag, per our own data rules. Anomaly detection is planned as simple statistics (per-category IQR/z-score outlier flags, moving-average trend), explicitly not framed as "AI price prediction" since we don't want to overclaim. Today, this is a designed rule, not a shipped feature — the `price_intelligence_service` is currently a stub.

**Q12: What's your database schema look like — did you actually think through the data model?**
A: Yes — core entities include collectors, material_categories, lots (with a status lifecycle DRAFT → ESTIMATED → MATCHED → HANDED_OVER → CONFIRMED → PAID/DISPUTED), lot_photos, recyclers, recycler_rates, prices (with a `source_type` of field/recycler/synthetic), handovers (with a `record_hash`), and ledger_entries (payment vs. due, cash vs. UPI). This is documented in `CONTEXT.md` and largely reflected in the SQLAlchemy models under `backend/src/models/`.

**Q13: Is there an actual Android app I can install right now?**
A: Not yet — be direct about this. The `collector_app/` folder today is an Expo package scaffold plus a detailed implementation guide (`docs/ANDROID_APP.md`) covering setup, permissions, offline queueing and sync. If asked to demo the collector side live, demo through the **recycler portal + backend API** (e.g. Swagger/OpenAPI docs from FastAPI, or Postman) rather than claiming a working phone app exists.

**Q14: What's your test coverage like — did you actually test this?**
A: The backend has a real pytest suite (`backend/tests/`) covering config, lots, recycler portal endpoints, collector auth/profile, matching, and pricing, running against SQLite for speed. [Note: we could not execute the suite in this offline analysis environment — run `PYTHONPATH=backend python -m pytest backend/tests -q` yourself before the demo and know the current pass count.] Be ready to say honestly how many tests pass today rather than guessing.

**Q15: Multi-tenancy / security — how do you handle auth and roles?**
A: JWT access + refresh tokens (`python-jose`), role field on the user model (`COLLECTOR`, `RECYCLER_ADMIN`, etc.), and OTP-based passwordless login for collectors — deliberately no email/password, per the problem statement's low-literacy constraint. OTP delivery itself is currently mocked (fixed code `123456`) for the demo; production would need a real SMS/OTP gateway, which the README explicitly calls out as an integration still required.

**Q16: What would break if 1,000 collectors used this simultaneously?**
A: Honestly, we haven't load-tested. SQLite is dev/test-only; Postgres is the intended production store. The current stubs (matching, pricing) return trivial/empty data so they wouldn't show real bottlenecks yet. If pressed, name what you'd add: connection pooling, a queue for sync ingestion, and caching for the price board — reasonable next steps, not built today.

**Q17: Why do you have two backend folders and two recycler-portal folders?**
A: Answer honestly using Section 2 — a merge of two contributors' prototypes during a repo restructuring (documented in our own `IMPLEMENTATION_PLAN.md`), and we haven't finished deleting the superseded `apps/` folder. The versions in `backend/` and `recycler_portal/` are the ones wired into `pnpm-workspace.yaml` and the ones we run.

**Q18: Blockchain — are you using blockchain for traceability?**
A: No, and deliberately not. `CONTEXT.md` explicitly lists blockchain as something we are **not** doing for the MVP. We use a simple SHA-256 hash chain of custody events instead — cheaper, no gas fees, easy to explain, and sufficient for a tamper-evident (not tamper-proof-at-blockchain-level) receipt.

**Q19: What languages does the app actually support today?**
A: `packages/i18n` has real locale files for English, Hindi, and Marathi (`en.json`, `hi.json`, `mr.json`) with translation keys for navigation, statuses, lot fields, auth, and hazard warnings — this part is genuinely built, not just planned.

**Q20: What's next on your roadmap if you had 3 more months?**
A: In priority order: (1) train and ship the on-device TFLite classifier on a larger, real field dataset, (2) implement the price intelligence and matching services (currently stubs) with the transparent formula already designed, (3) build the actual Expo/React Native collector app per `docs/ANDROID_APP.md`, (4) real SMS/OTP integration, (5) clean up the duplicate `apps/` scaffolding.

---

## 6. Things to actively avoid saying in the pitch

- Don't say "blockchain" — you explicitly chose not to use it.
- Don't say "our AI model is trained/deployed" — it isn't yet; say "designed and data-validated."
- Don't say "Node.js backend" or mention Fastify/NestJS/PostGIS/Redis/MinIO/Kubernetes/Terraform/UPI-escrow — none of that exists in your working code; it only appears in an aspirational architecture doc.
- Don't claim regulatory/EPR compliance — you are explicitly a "verifiable receipt," not a legal manifest.
- Don't claim real SMS OTP delivery works — the OTP is currently mocked.
- Don't claim there's a working native Android app — there's a scaffold and an implementation plan.

## 7. Things you can say with full confidence

- Real async FastAPI backend with JWT auth, a working lot-creation flow with live price-band lookups and SHA-256 custody hashing.
- A real, fairly built Next.js 14 + Tailwind recycler portal (login, dashboard, materials, handover, payment, ledger).
- A genuinely well-thought-out, documented data model and dataset registry with honesty tags distinguishing field/recycler/synthetic data, including real CC-BY-4.0 field images.
- A deliberate, defensible offline-first and low-literacy-first design philosophy, written down and followed (not just claimed).
- Multilingual (English/Hindi/Marathi) UI text tokens already implemented.
- A clear, honest scoping decision: no blockchain, no fake compliance claims, cash-first payments.

---

*Prepared from a direct static analysis of the `Ecobridge-main.zip` repository contents (backend source, frontend pages, package manifests, datasets, and internal docs) on the date of this session.*
