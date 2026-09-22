# Android collector app

The collector app is an Expo/React Native client for creating collection lots while offline and synchronising them with the EcoBridge API when connectivity returns.

## Create or restore the app

1. Install Node.js 18+ and pnpm 9+, then install Android Studio, the Android SDK, an emulator, and (on Windows) set `ANDROID_HOME` to the SDK directory.
2. From the repository root run `pnpm install`.
3. Enter `collector_app` and run `pnpm start`. Press `a` to open the Android emulator, or scan the Expo QR code with Expo Go.
4. For a native development build, run `npx expo prebuild`, then `npx expo run:android`. Keep the generated native directories out of source control unless native configuration is intentionally maintained.

If starting from an empty directory, run `npx create-expo-app@latest collector_app --template blank-typescript`, keep the generated `package.json`, and add `expo-router` (or use a simple `App.tsx` navigator). Do not copy a second partner snapshot into this repository.

## Backend integration

Set `EXPO_PUBLIC_API_URL` to the reachable backend URL (for an emulator, `http://10.0.2.2:8000`; for a physical device, use the development machine's LAN IP). Use the existing FastAPI routes:

- `POST /api/v1/auth/otp/send` and `POST /api/v1/auth/otp/verify` for collector authentication.
- `POST /api/v1/lots` to create a lot, including `lot_code`, GPS, `offline_created_at`, item weights, hazard classification, and proof images.
- `GET /api/v1/lots` to refresh the collector's server state.

Attach `Authorization: Bearer <access_token>` to every authenticated request. Store the access and refresh tokens in `expo-secure-store`.

## Offline-first workflow

Persist a queue in SQLite or AsyncStorage with a client-generated `lot_code` and `offline_created_at`. Capture photos and location locally, hash each image before upload, and show a pending-sync state. A background task should retry uploads with exponential backoff, treat a successful response as an acknowledgement, and leave failed records available for manual retry. Never silently discard a lot or overwrite a newer server record.

Request camera, location, and media-library permissions at runtime. Display hazard guidance before collection, support Hindi/Marathi/English labels through `packages/i18n`, and provide a clear consent and privacy notice. Test airplane mode creation, app restart, duplicate retry, expired tokens, and a partially uploaded image before shipping an APK or Play Store bundle.
