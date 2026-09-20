# @ecobridge/collector-mobile 📱

The **Collector Mobile App** is an offline-first mobile application built with React Native and Expo, designed for informal e-waste collectors, scrap aggregators, and *kabadiwalas*.

## Key Capabilities
- **Zero-Network Usability:** Fully functional offline using SQLite / WatermelonDB.
- **Edge AI Vision:** Real-time on-device classification of electronic components and hazardous conditions using INT8 quantized YOLOv8-nano via TensorFlow Lite.
- **Audio-Visual Guidance:** High-contrast, icon-driven interface with localized audio prompts in multiple vernacular languages.
- **Net-Earning Optimization:** Calculates estimated earnings net of transportation costs to nearby verified recyclers.
- **Offline QR Generation:** Creates tamper-proof cryptographically signed lot passes for scanning at recycler gates.

## Development
```bash
# Start Expo development server
pnpm --filter @ecobridge/collector-mobile start

# Run on Android emulator / connected device
pnpm --filter @ecobridge/collector-mobile android

# Run on iOS simulator (macOS only)
pnpm --filter @ecobridge/collector-mobile ios
```
