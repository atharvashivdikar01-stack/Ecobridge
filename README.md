# EcoBridge (कबाड़ीवाला कनेक्ट / Informal E-Waste Bridge)

> **Empowering informal e-waste collectors with offline-first on-device AI, fair pricing, vernacular voice guidance, and tamper-evident cryptographic traceability to certified recyclers.**

---

## 1. Executive Summary & Core Mission

EcoBridge bridges the gap between India's informal e-waste workforce (*kabadiwalas*, waste pickers, scrap aggregators) and CPCB-certified formal recyclers. 

Informal waste pickers collect over 90% of India's electronic scrap but face opaque pricing, lack of formal tax compliance, hazardous material risks, and language barriers. EcoBridge solves this with:
1. **Offline-First Mobile AI**: On-device classification of e-waste scrap using MobileNetV2 TensorFlow Lite.
2. **Fair Benchmark Pricing & Indian Tax Compliance**: Real-time pricing bands, automatic Indian 5% GST computation (HSN 8548/8549, 2.5% CGST + 2.5% SGST), and physical cash denomination counter.
3. **Voice-First Vernacular Accessibility**: Marathi, Hindi, and English voice prompts powered by pre-recorded `.ogg` studio files with intelligent single-instance Android TTS fallback.
4. **Deterministic Traceability & Audit Trail**: Every batch transition computes a SHA-256 tamper-evident custody hash linking collector, weighbridge slip, tax invoice, and recycler.

---

## 2. Key Features & Recent Upgrades

### 🤖 On-Device AI Scrap Classifier (Embedded TFLite)
- **Model**: `mobilenet_scrap_v1.tflite` (2.5 MB) deployed directly in `collector_app/app/src/main/assets/`.
- **Inference**: On-device MobileNetV2 taking `[1, 224, 224, 3] float32` normalized camera bitmaps.
- **Scrap Classes**:
  1. `CRT Monitors & TVs` (Hazardous)
  2. `LCD / LED Panels` (Warning)
  3. `Printed Circuit Boards (PCBs)` (High Value / Warning)
  4. `Copper Cables & Wires` (Normal)
  5. `Batteries` (Hazardous)
  6. `Motors & Magnet Assemblies` (Normal)
  7. `Mixed E-Waste Plastics` (Normal)
  8. `Other Electronic Scrap` (Normal)
- **UI Experience**: Instant top-3 confidence prediction cards, safety hazard alerts before pricing, and a 3-button confirmation bar (*Scan Again*, *Choose Other Category*, *Confirm*).

### 🗣️ Vernacular Language & Studio Voice Engine
- **Full Localization**: Complete string parity across Marathi (मराठी), Hindi (हिन्दी), and English (en).
- **Clean Context Switching**: `ContextWrapper` implementation in `BaseActivity` with immediate task recreation for seamless language switching across the entire app.
- **Audio-First Design**: Dual-mode audio pipeline:
  - **Real Voice Audio (`.ogg`)**: High-fidelity human voice prompts placed in `collector_app/app/src/main/res/raw/`.
  - **Automated TTS Fallback**: Singleton `AudioPromptManager` configured at `0.95x` speech rate for noisy scrap-yard conditions, with automatic Devanagari fallback when Marathi speech data is missing.
- **Voice Artist Documentation**: Includes `EcoBridge_Voice_Recording_Script_For_Voice_Artist.docx` (non-technical Word document with phonetic scripts and check-off tables) and `collector_app/VOICE_RECORDING_SPECIFICATION.md`.

### 💰 Indian GST & Cash Denomination Module
- **5% Reverse-Charge GST**: Computes base scrap value, 2.5% CGST, and 2.5% SGST under HSN 8548/8549.
- **Tax Invoice Generation**: Formats compliant invoice numbers (`TXI-YYYY-STATE-XXXXXX`).
- **Cash Denomination Counter**: Physical scrap yards operate primarily in cash. The app provides a live note counter (₹500, ₹200, ₹100, ₹50, ₹20, ₹10, ₹5, coins) with:
  - Greedy auto-fill change algorithm for instant note distribution.
  - Live green/amber match badges comparing entered cash against invoice total.

### ⛓️ Tamper-Evident Traceability (Chain of Custody)
- Offline lot creations and physical handovers generate an immutable SHA-256 digital fingerprint:
  `SHA-256(LOT_UUID | RECYCLER_ID | WEIGHT | GROSS | TAX | TOTAL | INVOICE | PAYMENT_MODE | TIMESTAMP)`
- When a CPCB-verified recycler confirms receipt on the web portal, an append-only `CustodyEvent` is recorded with `previous_event_hash` linkage.

---

## 3. Repository Architecture

```text
Ecobridge-repo/
├── collector_app/               # Native Android Client (Java 17, Room, WorkManager, TFLite)
│   ├── app/src/main/assets/     # mobilenet_scrap_v1.tflite & labels.txt
│   ├── app/src/main/java/       # MVVM, Room Entities, DAOs, AI Classifier, Audio Engine
│   ├── app/src/main/res/        # Vernacular strings (values, values-hi, values-mr), layouts
│   └── VOICE_RECORDING_SPECIFICATION.md # Developer audio specification
├── backend/                     # FastAPI Async Backend (Python 3.11+, SQLAlchemy, Pydantic)
│   ├── src/
│   │   ├── api/v1/endpoints/    # auth, lots, sync, recyclers, recycler_portal, pricing
│   │   ├── core/                # config, database, bootstrap, security
│   │   ├── models/              # SQLAlchemy async models (User, Lot, Handover, Custody)
│   │   └── services/            # LotService, AuthService, OTPService
│   └── tests/                   # pytest test suite
├── recycler_portal/             # Certified Recycler Portal (Next.js, Tailwind CSS)
├── admin_dashboard/             # Platform & Regulator Admin Dashboard (Next.js)
├── packages/                    # Shared workspace libraries (api-contracts, crypto-traceability)
├── scripts/
│   ├── test_end_to_end_flow.py  # Automated 3-phase closed-loop verification test
│   └── generate_voice_script_docx.py # Voice artist Word script generator
└── EcoBridge_Voice_Recording_Script_For_Voice_Artist.docx # Voice artist Word document
```

---

## 4. Getting Started & Local Development

### Prerequisites
- **Python**: 3.11+ (recommended: `uv` or standard `python -m venv`)
- **Android**: Android Studio Hedgehog+ or SDK Platform 34, JDK 17
- **Node.js**: Node 18+ and `pnpm` (version >= 9)

---

### Step 1: Start the Backend Service

1. Open PowerShell and navigate to `backend/`:
   ```powershell
   Set-Location backend
   uv venv --python 3.11
   .venv\Scripts\activate
   uv pip install -r requirements.txt
   ```
2. Initialize the local SQLite catalog & seed data:
   ```powershell
   python -m scripts.init_local_db
   ```
3. Start the FastAPI development server:
   ```powershell
   uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload
   ```
   API Documentation is available at `http://127.0.0.1:8000/docs`.

---

### Step 2: Build & Run the Android Collector App

1. Open PowerShell and navigate to `collector_app/`:
   ```powershell
   Set-Location collector_app
   .\gradlew.bat assembleDebug
   ```
   The compiled APK will be produced at:
   `collector_app/app/build/outputs/apk/debug/app-debug.apk`

2. Install to a running Android emulator or USB-connected phone:
   ```powershell
   .\gradlew.bat installDebug
   ```

> [!NOTE]
> - **Emulator Networking**: The debug build automatically connects to `http://10.0.2.2:8000/` (host machine alias).
> - **Physical Device**: Connect phone and computer to the same Wi-Fi, find your LAN IP (e.g. `192.168.1.50`), and build with:
>   `.\gradlew.bat assembleDebug -PECOBRIDGE_API_URL=http://192.168.1.50:8000/`
> - **Zero-Barrier Mobile Login**: Enter any 10-digit Indian phone number (e.g. `9876543210`). The dev OTP is `123456`.

---

### Step 3: Run the Recycler Web Portal

1. Navigate to `recycler_portal/`:
   ```powershell
   Set-Location recycler_portal
   pnpm install
   $env:NEXT_PUBLIC_API_URL = 'http://127.0.0.1:8000/api/v1'
   pnpm run dev
   ```
2. Open `http://localhost:3001` in your browser. Use Demo Login with role **Recycler** to inspect incoming scrap handovers, audit weighbridge data, and confirm custody.

---

## 5. Verification & Testing Suite

All layers of the platform are continuously verified:

### 1. Automated 3-Phase Closed-Loop Integration Test
Validates the entire collector-to-recycler workflow against the ASGI server:
```powershell
uv run --python 3.11 python scripts/test_end_to_end_flow.py
```
**Test Workflow Covered:**
- Collector OTP Authentication (`/api/v1/auth/otp/verify`)
- Offline Lot Sync (`/api/v1/sync/batch`)
- Handover Creation with GST & SHA-256 Hash (`/api/v1/sync/handovers`)
- Recycler Verification (`/api/v1/recycler-portal/handovers/{ref}/confirm`)
- Tamper-Evident `CustodyEvent` append-only block verification
- Closed-Loop Collector Status Refresh (`/api/v1/sync/status`)

### 2. Backend Pytest Suite
```powershell
uv run --python 3.11 pytest backend/tests
# Result: 18 passed in 2.42s
```

### 3. Android Clean Build Verification
```powershell
cd collector_app
.\gradlew.bat compileDebugJavaWithJavac
# Result: BUILD SUCCESSFUL
```

---

## 6. Real Voice Recording Instructions

To add studio voice recordings to the Android app:
1. Provide `EcoBridge_Voice_Recording_Script_For_Voice_Artist.docx` to your voice artist friend. It contains simple, non-technical instructions and exact phonetic scripts for Hindi, Marathi, and English.
2. Export the recordings as mono OGG Vorbis (`.ogg`), 44.1 kHz, 16-bit.
3. Place the exported `.ogg` files directly into:
   `collector_app/app/src/main/res/raw/`
4. Rebuild the app. The app automatically detects real voice files; if any file is missing, it falls back to TTS without errors.

---

## 7. Production Deployment & Security

- **Database**: In production, configure PostgreSQL 16 with PostGIS:
  `DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/ecobridge`
- **Reverse Proxy**: Place FastAPI and Next.js behind Nginx or Caddy with automated Let's Encrypt TLS certificates.
- **Security Invariant**: Never disable cryptographic hash validation or commit cleartext production secrets.

---

## 8. Strategic Roadmap: Urban Mining, Deep Material Intelligence & Gamification

EcoBridge is expanding into an **AI-driven Urban Mining & Circular Economy Platform**:

1. **Android Core Roadmap**:
   - **GPS Geotagging**: Attach fine-accuracy latitude/longitude (`ACCESS_FINE_LOCATION`) to `LotEntity` for regional scrap mapping and fraud prevention.
   - **Debug-Only Cleartext**: Production release builds enforce TLS 1.3 HTTPS; cleartext traffic isolated to `app/src/debug/AndroidManifest.xml`.
   - **Visual Sync Indicators**: Status badges (`PENDING`, `SYNCING`, `SYNCED`, `FAILED`) in transaction lists.
2. **Deep Material Intelligence & Elemental BOM**:
   - **Multi-Task Computer Vision**: Upgrading from single-label MobileNet to hierarchical identification (Device $\rightarrow$ Subcategory $\rightarrow$ Physical Condition $\rightarrow$ Elemental Bill of Materials).
   - **Rare Metal Recovery Engine**: Computes exact gram/kilogram yields of Gold (Au), Silver (Ag), Copper (Cu), Palladium (Pd), Cobalt (Co), and Lithium (Li).
   - **Hazard Matrix**: Prioritizes safety advisories (swollen batteries, hydrofluoric acid, toxic CRT lead oxide, mercury switches) before financial estimates.
3. **Recycler Smelting Economics**:
   - Calculates real-time gross recovery value using live commodity market rates (MCX / LME) and hydrometallurgical extraction efficiencies.
   - Automated CPCB EPR compliance certification for electronics manufacturers.
4. **Collector Incentive Flywheel**:
   - **Daily Quota Rewards**: Direct cash / UPI bonuses for daily volume milestones (e.g. 15 kg/day $\rightarrow$ +₹50).
   - **EPR Green Dividend**: Passing ₹3–5/kg of corporate EPR compliance revenue directly to the informal waste picker.
   - **Aggregator Hub (*Kabadi Dukaan*) Franchising**: Transforming neighborhood scrap shops into certified collection hubs with a 1.5% aggregation fee.

---

## 9. DPDP Act (2023) Compliance, Privacy Architecture & User Rights

EcoBridge complies strictly with India's **Digital Personal Data Protection Act (DPDP Act 2023)**:

- **Audio-Visual Vernacular Consent**: Transparent notices in Marathi, Hindi, and English with voice audio playback for low-literacy informal collectors.
- **Strict Data Minimization**: Zero collection of Aadhaar numbers, biometric face data, contacts, or SMS logs. Only phone (authentication), GPS (scrap origin), and photos (material audit) are collected.
- **Child Labor Prevention**: Mandatory age declaration ($\ge 18$) to prevent informal child labor in e-waste processing.
- **Right to Erasure & DPO Contact**: Collectors can delete personal profiles; statutory audit hashes remain anonymized for regulatory compliance. Dedicated DPO grievance escalation with a 7-day SLA.
- **Modern Android Permissions**: Just-In-Time rationale dialogs for `CAMERA`, `ACCESS_FINE_LOCATION` (in-use only), and `POST_NOTIFICATIONS` with scoped storage (zero external storage access).


