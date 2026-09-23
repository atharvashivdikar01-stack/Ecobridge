# ECOBRIDGE Collector Android App

Native Android collector app using Java, XML layouts, Room, WorkManager, CameraX,
and offline TTS. Lots and handovers are saved locally before any network attempt.

## Build

Install Android SDK Platform 34 and JDK 17. `assembleDebug` targets the localhost
Android Emulator API at `http://10.0.2.2:8000/`; clear-text is enabled only for the
debug manifest. Pass a TLS endpoint for release-like builds with
`-PECOBRIDGE_API_URL=https://api.example.in/`.

For local testing, start `../backend` as documented in the root README, sign in with
any phone number and OTP `123456`, and choose `Local Test Recycler`. Lots and handovers
are queued in Room; handovers become confirmed only after the server-side recycler action.

The local OTP, recycler, rates, and HTTP endpoint are demo-only. Release builds must use
HTTPS, real OTP delivery, and independently verified recycler data.
