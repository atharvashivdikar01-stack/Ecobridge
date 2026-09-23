# EcoBridge (Kabadiwala Connect)

EcoBridge is an offline-first e-waste collection platform for informal collectors and authorised recyclers. The collector records a lot on an inexpensive Android phone, even without connectivity; the app later syncs it to the backend, where a recycler can confirm custody. The product goal is transparent collection records and better price access, not a generic scrap marketplace.

## Current working path

The canonical implementation is:

1. `collector_app/` native Android collector app (Java/XML, Room, WorkManager).
2. `backend/` FastAPI service used for the local integration environment.
3. SQLite for local testing; PostgreSQL is the intended deployed database.

The verified localhost flow is:

```text
Collector OTP login -> create Room lot + photo offline -> sync lot + photo
-> create/sync handover -> verified recycler confirms custody -> payment
-> collector pulls confirmed/paid status into Room
```

Lots, handovers, and photos are stored locally first. Network work is performed by
WorkManager; uploads are idempotent and photo bytes are checked against the SHA-256
hash calculated on the device.

## Repository map

| Path | Role | Status |
| --- | --- | --- |
| `collector_app/` | Canonical native Android collector app | Active |
| `backend/` | Active FastAPI localhost backend and tests | Active |
| `apps/api-server/` | Parallel newer FastAPI implementation | Not wired to the native app; do not use for local demo |
| `apps/collector-mobile/` | Expo collector prototype | Legacy prototype |
| `recycler_portal/` | Canonical Next.js recycler portal | Active |
| `apps/recycler-portal/` | Earlier portal experiment | Legacy / not wired |
| `ai/train_ewaste_classifier.ipynb` | Google Colab training and TFLite export | Run to produce the on-device model |
| `docs/`, `datasets/`, `infra/` | Product, data, and deployment reference material | Reference / future work |

Read [EXPLANATION.md](EXPLANATION.md) for current capabilities, known limits, and the implementation plan.

## Run locally

Prerequisites: Python 3.11+, Android SDK Platform 34, JDK 17, and an Android emulator.

Start the backend in one PowerShell window:

```powershell
Set-Location backend
python -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
$env:DATABASE_URL = 'sqlite+aiosqlite:///./ecobridge_local.db'
.\venv\Scripts\python.exe -m scripts.init_local_db
.\venv\Scripts\python.exe -m uvicorn src.main:app --host 127.0.0.1 --port 8000
```

In a second window, build and install the debug app on a running emulator:

```powershell
Set-Location collector_app
.\gradlew.bat installDebug
```

The debug APK uses `http://10.0.2.2:8000/`, Android Emulator's address for the host machine. It is enabled only in the debug manifest. Release builds default to an invalid HTTPS endpoint until supplied with `-PECOBRIDGE_API_URL=https://your-api.example/`.

For local login, enter any 10-digit mobile number, request an OTP, and enter `123456`. This OTP is development-only and must never be enabled outside localhost.

The APK is at `collector_app/app/build/outputs/apk/debug/app-debug.apk` after a successful build.

### Recycler portal

```powershell
Set-Location recycler_portal
pnpm install --frozen-lockfile
$env:NEXT_PUBLIC_API_URL = 'http://127.0.0.1:8000/api/v1'
pnpm run dev
```

The portal runs on port 3001 and the backend permits both local ports 3000 and 3001.

### On-device AI model

There is no trained model binary in this repository. Upload `datasets/ai_ml/vision`
as `vision.zip` to [ai/train_ewaste_classifier.ipynb](ai/train_ewaste_classifier.ipynb)
in Google Colab, run every cell, then copy the downloaded `mobilenet_scrap_v1.tflite`
and `labels.txt` to `collector_app/app/src/main/assets/`. The model runs fully offline.
Until the model is added, the app intentionally requires manual material selection.

## Verification

Verified on this workstation:

- Backend tests: `18 passed`.
- Native Android debug build: `assembleDebug` succeeds.
- Recycler portal production build: `pnpm run build` succeeds.
- End-to-end test: native-style offline lot sync, SHA-256 photo upload, handover,
  custody confirmation, settlement, and collector status pull.

Not yet verified: physical-phone networking, real recycler identities, production PostgreSQL migrations, trained model accuracy, real OTP delivery, payment-provider integration, and hosted HTTPS deployment.

## Security rules

- Do not commit `.env`, `local.properties`, APKs, databases, keys, certificates, or production credentials.
- Keep cleartext HTTP debug-only. Production uses HTTPS.
- Treat all seeded rates and recyclers as demo data unless independently verified.
- A traceability record supports auditing; it is not an EPR certificate or a regulatory manifest.
