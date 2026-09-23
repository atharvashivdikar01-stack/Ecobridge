# @ecobridge/collector-mobile 📱

The **Collector Mobile App** is an offline-first mobile application built with React Native and Expo, designed for informal e-waste collectors, scrap aggregators, and *kabadiwalas*.

## Included workflow
- OTP login with access and refresh tokens in `expo-secure-store`.
- Dashboard with server lot history and explicit pending/failed sync states.
- Offline lot creation with a client-generated lot code, AsyncStorage queue, location capture, proof photo capture, and hazard warning.
- Token refresh and authenticated API calls for the FastAPI `/api/v1` routes.

## Development
```bash
# Start Expo development server
pnpm --filter @ecobridge/collector-mobile start

# Run on Android emulator / connected device
pnpm --filter @ecobridge/collector-mobile android

# Run on iOS simulator (macOS only)
pnpm --filter @ecobridge/collector-mobile ios
```

Copy `.env.example` to `.env` and set `EXPO_PUBLIC_API_URL`. Android emulators reach a local API at `http://10.0.2.2:8000/api/v1`; physical devices need the development machine's LAN address.

The current lot form uses the backend's generic material identifier as a safe minimal default. Taxonomy selection, image upload storage, background task scheduling, and device-level cryptographic image hashing remain follow-up work; queued records are retained for manual retry and are never silently discarded.
