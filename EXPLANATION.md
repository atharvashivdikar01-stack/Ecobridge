# EcoBridge: current state and future plan

Last updated: 2026-09-23

## What we are building

EcoBridge is a practical bridge between informal e-waste collectors and formal recyclers. A collector should be able to photograph and record a scrap lot without internet, get a transparent local estimate, retain proof of what was handed over, and sync the record later. A recycler should be able to verify the incoming handover before payment is settled.

The value is not a marketplace screen by itself. The value is an offline-first, low-literacy collection workflow that preserves evidence and does not force collectors into unnecessary KYC or digital payments.

## What is implemented now

### Android collector app

The canonical app is `collector_app/`.

- Native Android Java/XML UI designed for low-end devices.
- Room stores lots and handovers locally.
- WorkManager retries sync when connectivity is available.
- CameraX captures lot photos; the app computes local hashes.
- Audio uses Android TTS as a fallback; bundled audio/model assets must be real before claiming field readiness.
- OTP access tokens are saved in encrypted preferences.
- Debug builds reach localhost through Android Emulator at `10.0.2.2:8000`.

The app is usable as a collector demo. It is not yet a field-ready regulated collection product.

### Backend

The active local backend is `backend/`, not `apps/api-server/`.

- FastAPI and SQLAlchemy async.
- SQLite local database seeded by `backend/scripts/init_local_db.py`.
- PostgreSQL remains the production target.
- OTP endpoint for local testing uses code `123456`.
- Native lot sync is idempotent by collector and short code.
- Native handover sync requires that the collector's lot is already on the server.
- A verified recycler confirmation endpoint changes handover custody to `CONFIRMED` and appends a custody event.

### Handover state today

```text
Phone creates local handover
  -> handover sync creates PENDING_RECYCLER_CONFIRMATION record
  -> addressed verified recycler confirms it
  -> custody is CONFIRMED, payment is still PENDING
  -> future authorised settlement records payment and updates the collector ledger
```

This separation is intentional. A handover and a payment are different facts. The app must not claim cash, UPI, or bank settlement without a server record from the recycler-side flow.

## Evidence from the latest local check

- `backend`: 17 automated tests pass.
- `collector_app`: debug APK compiles successfully.
- Local HTTP flow passed: health check, OTP, lot sync, duplicate retry, handover sync, and recycler confirmation.

The test environment uses only local SQLite and fake/seeded recycler data. Passing this test does not verify any government registration, real market rate, payment, or EPR process.

## Known gaps

| Area | Current state | Required before production |
| --- | --- | --- |
| Recycler UI | API exists; portal is not wired to confirmation | Build and test recycler confirmation screen |
| Payment | Remains pending after confirmation | Authorised settlement endpoint, immutable receipt, ledger update |
| Photos | Local capture/hash only | Secure upload, server hash verification, object storage, retry queue |
| AI | Optional TFLite path; no verified field model claim | Validate a real dismantled-scrap model and its accuracy |
| Recycler data | Local demo seed | Verify recycler authorisations and source rates |
| OTP | Fixed local development OTP | Use real provider, abuse limits, audit logging |
| Database | SQLite local development | PostgreSQL migrations, backups, monitoring |
| Network | Emulator localhost only | Physical-device offline/online test and HTTPS deployment |
| Duplicate stacks | Two API generations and two mobile approaches exist | Choose, merge, or remove the unused generations |

## Recommended execution order

### Phase 1: complete the demo flow

1. Build recycler portal confirmation UI over the existing confirmation API.
2. Add a recycler settlement action that records cash/UPI reference, changes payment to paid, and creates the collector ledger entry.
3. Show the collector the confirmed and paid status after a sync refresh.
4. Run the collector and recycler scenario on an emulator with deliberately disabled/re-enabled networking.

### Phase 2: make data trustworthy

1. Replace the local demo recycler with field-verified recycler records.
2. Add rates with source, date, area, and clear synthetic/demo labels.
3. Upload photos separately from lot metadata; validate SHA-256 on the server.
4. Treat the on-device model as a suggestion and require manual category confirmation below a confidence threshold.

### Phase 3: prepare deployment

1. Create PostgreSQL migrations from the active `backend/` models.
2. Configure production environment variables, strong JWT key, real OTP provider, and empty `TEST_OTP`.
3. Deploy behind TLS; set the Android release build URL through `ECOBRIDGE_API_URL`.
4. Add backups, readiness checks, rate limits, and server-side audit logging.
5. Test on a physical low-cost Android device with poor connectivity.

## How to use localhost today

Start the API:

```powershell
Set-Location backend
$env:DATABASE_URL = 'sqlite+aiosqlite:///./ecobridge_local.db'
.\venv\Scripts\python.exe -m scripts.init_local_db
.\venv\Scripts\python.exe -m uvicorn src.main:app --host 127.0.0.1 --port 8000
```

Run an Android Emulator and install the debug app:

```powershell
Set-Location collector_app
.\gradlew.bat installDebug
```

Use any 10-digit phone number and OTP `123456`. Choose **Local Test Recycler** for the local handover scenario. The recycler confirmation API is intentionally a developer-facing workflow until the portal UI is connected.

## Plain-language pitch

"EcoBridge lets a kabadiwala record e-waste even when offline, keep evidence of the lot, and bring that record to a verified recycler. When the phone reconnects, the record syncs without duplication. The recycler confirms custody separately from payment, so the collector's ledger reflects actual verified events rather than promises."
