# CONTEXT.md — Kabadiwala Connect (SIH 2026, PS 26229)

> Single source of truth for the team AND for AI assistants. Keep it short and current.
> Anything marked **PROPOSED** is not final: change it through a pull request once the team agrees.
> Last updated: <DATE> by <NAME>

## 1. What we are building

A vernacular (Marathi + Hindi), low-literacy, offline-first Android app that lets informal scrap collectors:
photograph and log lots of e-waste, see a fair value estimate, find nearby AUTHORIZED recyclers,
complete a traceable handover, and keep a simple earnings ledger. Plus a recycler-side web interface.

Problem statement: SIH 2026, PS 26229 "Kabadiwala Connect – Bringing the Informal Collector into the
Formal Recycling Chain" (Ministry of Mines / JNARDDC, Software, Clean & Green Technology).

Hard requirements from the PS:
- Works offline and syncs later; small APK and low RAM (entry-level Android)
- Marathi + Hindi at minimum; pictorial / audio guidance
- Cash payments allowed (digital optional); minimal personal data
- Structured datasets: materials, prices, recyclers, transactions, traceability, collectors
- Recycler-side interface, field research with at least 2 real collectors/aggregators, live demo, unit economics

Legal positioning: the handover record is a verifiable receipt / traceability aid, NOT a legal manifest.
Never claim regulatory compliance in the app or the pitch.

## 2. Users

- Collector (kabadiwala): low literacy, cheap Android phone, patchy internet, Marathi/Hindi. Icons + audio first, text second.
- Recycler / aggregator: sees incoming lots, confirms handovers, updates rates. Uses a web page (phone or laptop).
- Admin (team, for demo): manages prices, recyclers and seed data.

## 3. MVP "golden path" (must work offline, end to end, before anything else)

1. Choose language (Marathi / Hindi) -> icon-first home screen with audio prompts
2. New lot: photo -> category (AI suggests, user confirms from icon grid) -> weight -> instant value estimate
3. Price board: current rates per category with spoken price + trend arrow
4. Recycler ranking: authorized, accepts this category, nearby, best rate
5. Handover record: photos, weight, timestamp, GPS, unique code -> recycler confirms
6. Earnings ledger: cash by default, pending dues visible
7. Sync when internet returns

Tier 2: safety cards (picture + audio), anomaly flags on odd prices, price-trend charts.
Tier 3 (stretch): WhatsApp/SMS receipt, missed-call price line, optional UPI "mark as paid".
NOT doing: blockchain, real payment gateway, iOS, email/password login.

## 4. Architecture (AGREED)

- Monorepo: pnpm workspaces + Turborepo for build orchestration
- Collector app: React Native / Expo offline-first client, SQLite / WatermelonDB, TensorFlow Lite (on-device classifier)
- Backend: Python + FastAPI + SQLAlchemy Async, REST JSON under /api/v1; SQLite in dev, PostgreSQL 16 when deployed
- Recycler portal: Next.js (App Router) + React + Tailwind CSS; Leaflet + OpenStreetMap for maps
- Admin dashboard: Next.js (App Router) + React + Tailwind CSS
- Shared packages: api-contracts (TypeScript + Zod), database, sync-engine, ai-core, crypto-traceability, ui, i18n, tsconfig, eslint-config
- Voice: pre-recorded Marathi/Hindi audio clips (numbers composed from clips); Android TTS only as fallback
- Fallback plan: if "photo -> save offline -> sync" is not working by the end of the tech spike,
  switch the collector app to a PWA (HTML/JS, service worker, IndexedDB) wrapped as an APK.

Offline-first rules:
- The phone is the source of truth for a lot until it is synced. Write to local SQLite first, always.
- IDs are UUIDv4 generated ON THE DEVICE, plus a short human-friendly code (6 chars) for the recycler.
- Sync = outbox queue + idempotent upserts (the same lot_id sent twice must not create duplicates).
- Photos: compress to about 150 KB (~800 px JPEG), upload separately with retry, store a SHA-256 hash.
- Price board is cached; always show a "last updated" time.
- Conflict rule: server wins for prices and recycler data; device wins for lot details until submitted.

## 5. Data model (PROPOSED)

All timestamps UTC ISO-8601, weight in kg, money in INR.

- collectors(collector_id, preferred_language, operating_area, created_at) — name/phone OPTIONAL
- material_categories(category_id, name_en, name_mr, name_hi, icon, hazard_level)
- lots(lot_id, short_code, collector_id, category_id, subcategory, description, condition, source_type,
  approx_weight_kg, estimated_value, quoted_price, final_sale_value, collected_at, lat, lng, status, synced_at)
- lot_photos(photo_id, lot_id, file_path, sha256, taken_at, uploaded)
- recyclers(recycler_id, name, address, lat, lng, contact, registration_no, authorization_status,
  service_area, pickup_available, updated_at)
- recycler_rates(recycler_id, category_id, offered_rate_per_kg, updated_at)
- prices(price_id, category_id, subcategory, area, recorded_at, buying_price, selling_price, unit,
  range_low, range_high, recycler_id NULL, source_type)   -- source_type: field | recycler | synthetic
- handovers(handover_id, lot_id, recycler_id, reference_no, weight_at_handover, lat, lng,
  handed_over_at, recycler_confirmed_at, record_hash, status)
- ledger_entries(entry_id, collector_id, handover_id, amount, entry_type, payment_mode, created_at)
  -- entry_type: payment | due ; payment_mode: cash | upi

Lot status: DRAFT -> ESTIMATED -> MATCHED -> HANDED_OVER -> CONFIRMED -> PAID (or DISPUTED)

Rules: never mix real and synthetic prices without source_type; never store unnecessary personal data.

## 6. AI/ML scope (be honest about limits)

- Material classifier: about 8 classes (CRT, LCD/LED panel, PCB, cables, batteries, motors/magnet assemblies,
  mixed plastics, other). TFLite on device. Low confidence -> ask the user to pick from the icon grid.
  Confirmed picks become new training data.
- Valuation v1: weight x recycler rate for that area x condition factor. Transparent formula, no ML.
- Recycler ranking: hard filters (valid authorization, accepts the material), then a weighted score
  (rate, distance, pickup availability).
- Anomalies / trends: per-category IQR or z-score rules, moving-average trend.
  Call it "trend detection", not "price prediction".
- Dataset honesty: document source, size, quality and limitations of every dataset. Label synthetic data as synthetic.

## 7. API sketch (PROPOSED)

- POST /api/v1/sync              batch upload of lots (idempotent by lot_id)
- POST /api/v1/lots/<id>/photos  photo upload
- GET  /api/v1/prices?area=&since=
- POST /api/v1/match             category, weight, lat, lng -> ranked recyclers
- POST /api/v1/handovers/<ref>/confirm
- GET  /api/v1/ledger?collector_id=

## 8. Coding conventions

General: small commits, clear names, comments for anything non-obvious.
Simple code beats clever code: everyone must be able to explain it.

Python / FastAPI:
- PEP 8, snake_case, one router per feature (prices, recyclers, lots, handovers).
- Async endpoints with SQLAlchemy async sessions. Pydantic schemas for all request/response.
- Config from environment (.env). Never commit secrets or API keys.

TypeScript / Next.js:
- Strict mode enabled. No `any` types — use `unknown` with Zod parsing or type guards.
- Use `@ecobridge/*` workspace packages for shared logic.
- All UI text via i18n translation tokens — no hardcoded English strings in views.

Git:
- Branches: feature/<name>-<thing>. main must always run. Every PR is reviewed by one other person.

## 9. Team and ownership (fill in)

- Lead / product / pitch: <name>
- Android A (lot creation, camera, ledger): <name>
- Android B (Room, sync, price board, audio): <name>
- Backend (Flask, DB, matching): <name>
- Web (recycler dashboard, admin): <name>
- Data / ML (datasets, classifier, trends, unit economics): <name>

## 10. Decisions log (newest first)

- <date> — <decision> — <why> — <who>

## 11. Open questions

- What do recyclers actually accept (whole units vs parts)? Ask during field research.
- Finale rules: what may be pre-built? Is AI-tool use restricted?
- Exact finale dates (November/December 2026).

## 12. Rules for AI assistants working in this repo

- Follow this file. If a request conflicts with it, say so instead of inventing a different design.
- Prefer the simplest solution that fits our stack; do not add libraries or frameworks without asking.
- Explain what generated code does in plain language so a beginner can defend it.
- Never invent price data, recycler details or registration numbers.
- Keep personal data minimal; never log photos, phone numbers or GPS in production code.
