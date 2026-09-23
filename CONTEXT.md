# EcoBridge context

Last updated: 2026-09-23

## Product

EcoBridge (SIH 26229, Kabadiwala Connect) helps informal e-waste collectors create an offline collection record, estimate value, identify recycler options, and make a tamper-evident handover record. The intended users are low-literacy collectors using low-cost Android phones, verified recyclers, and a small admin/demo team.

The platform must protect collector livelihoods and avoid overstating its legal role. It helps create traceability evidence; it does not issue EPR certificates or replace CPCB/SPCB documentation.

## Current architecture

```text
Native Android app (collector_app)
  Room local database -> WorkManager queued sync -> FastAPI backend
                                             -> SQLite locally / PostgreSQL when deployed
```

- `collector_app/` is the canonical collector app: Java, XML layouts, Room, WorkManager, CameraX, optional TensorFlow Lite, and Android TTS fallback.
- `backend/` is the active local FastAPI implementation. It has the test suite and the native sync compatibility endpoints.
- `apps/api-server/` is a separate backend generation. It is not the local-demo backend because its sync contract differs and its sync endpoint is an acknowledgement stub.
- `apps/collector-mobile/` is a legacy Expo prototype. Do not add new collector features there.
- Recycler portal folders are parallel UI work. The verified local recycler confirmation is currently available through the API endpoint, not a finished portal workflow.

## Verified implementation status

### Works locally

1. Debug Android app logs in via local OTP and stores its token using encrypted preferences.
2. Lots are written to Room first and retried through WorkManager.
3. `POST /api/v1/sync/batch` accepts native lots, maps their category to the local material catalog, persists them, and is idempotent by collector + short code.
4. `POST /api/v1/sync/handovers` stores a collector handover only after its lot is present on the server.
5. `POST /api/v1/recycler-portal/handovers/{reference_no}/confirm` permits only the addressed, verified recycler to confirm custody.
6. Confirmation appends a custody event. Payment remains `PENDING`; it is not fabricated by the client.

### Deliberate local-development settings

- Android debug base URL: `http://10.0.2.2:8000/` for Android Emulator.
- Local API host: `127.0.0.1:8000`.
- Local database: ignored SQLite file `backend/ecobridge_local.db`.
- Local OTP: `123456` only.
- Local Test Recycler ID: `00000000-0000-0000-0000-000000000101`; it is seed data, not a real recycler.

Cleartext HTTP is present only in `collector_app/app/src/debug/AndroidManifest.xml`. Release builds must use HTTPS.

## Important contracts

Native app routes used by the active backend:

- `POST /api/v1/auth/otp/send`
- `POST /api/v1/auth/otp/verify`
- `POST /api/v1/sync/batch`
- `POST /api/v1/sync/handovers`
- `POST /api/v1/recycler-portal/handovers/{reference_no}/confirm`

The phone's local UUID is not trusted as the server lot identity. A handover includes the lot's short code, which the server resolves under the authenticated collector. This prevents a local database ID from being mistaken for a server UUID.

## Non-negotiable rules

- Offline data is written locally before any network call.
- Retried sync must be idempotent.
- Never mark payment paid until an authorised server-side settlement operation records it.
- Do not invent recycler permits, rates, or AI classifications. Demo values must be visibly demo/unverified.
- Do not collect unnecessary KYC, GPS, or financial information.
- Keep secrets and generated local data out of Git.

## Next milestones

1. Build the recycler confirmation UI against the existing endpoint, then implement authorised payment settlement and collector ledger update.
2. Add migrations and run the active backend on PostgreSQL; retire or merge the duplicate backend generation.
3. Upload compressed photos separately, verify hashes server-side, and add retry/error states.
4. Replace demo recycler/rate data with verified field data and label price sources.
5. Test offline/online transitions on a physical low-cost Android device. Configure a debug LAN URL only for that test.
6. Add real OTP provider credentials, TLS, production secrets, backups, and deployment monitoring before hosting.

See [EXPLANATION.md](EXPLANATION.md) for a fuller explanation of the current state and delivery plan.
