# ECOBRIDGE (कबाड़ीवाला कनेक्ट / Informal E-Waste Bridge)

[![SIH 2026](https://img.shields.io/badge/SIH%202026-Problem%20Statement%2026229-16a34a.svg)](https://sih.gov.in)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI%20Async-009688.svg)](https://fastapi.tiangolo.com)
[![Next.js 14](https://img.shields.io/badge/Web%20Portals-Next.js%2014%20App%20Router-000000.svg)](https://nextjs.org)
[![Android](https://img.shields.io/badge/Mobile-Android%20Native%20(Java%2017)-3DDC84.svg)](https://developer.android.com)
[![TensorFlow Lite](https://img.shields.io/badge/AI%20Engine-TFLite%202.16.1-FF6F00.svg)](https://tensorflow.org/lite)
[![Alembic](https://img.shields.io/badge/Database-Alembic%20Migrations-purple.svg)](https://alembic.sqlalchemy.org)
[![DPDP Act 2023](https://img.shields.io/badge/Compliance-DPDP%20Act%202023-blue.svg)](https://www.meity.gov.in)

> **Empowering India's informal e-waste collectors (*kabadiwalas*, waste pickers, aggregators) with offline-first on-device AI, fair benchmark pricing, vernacular voice guidance, and tamper-evident cryptographic traceability to CPCB-certified formal recyclers.**

---

## 🏆 Judge Evaluation & Live Links

| Component | Target URL / Asset | Credentials |
|---|---|---|
| **Certified Recycler Portal** | `https://ecobridge-recycler-portal.vercel.app` *(or localhost:3000)* | Phone: `+919811111111` \| OTP: `123456` |
| **CPCB & Regulator Dashboard** | `https://ecobridge-admin-dashboard.vercel.app` *(or localhost:3002)* | Instant 1-Click Role Switcher |
| **Interactive OpenAPI Backend** | `https://ecobridge-backend.onrender.com/docs` *(or localhost:8000/docs)* | Fully interactive Swagger UI |
| **Installable Android APK (v1.0)** | [`release/EcoBridge-Collector-v1.0.apk`](release/EcoBridge-Collector-v1.0.apk) | Direct install on any Android 8.0+ device |
| **Deployment & Demo Script** | [`DEPLOY.md`](DEPLOY.md) | Complete 5-minute judge evaluation playbook |

---

## 1. Problem Statement & Mission (SIH 2026 PS 26229)

Over **90% of India's e-waste** is handled by the unorganized informal sector—informal waste pickers, scrap aggregators, and *kabadiwalas*. Despite being the backbone of material recovery, they face:
1. **Opaque, Predatory Scrap Pricing**: Middlemen exploit lack of price discovery, paying fractions of true secondary raw material value.
2. **Extreme Health Hazards**: Manual dismantling of CRT glass, swollen lithium batteries, and acid-leaching PCBs without safety warnings or PPE.
3. **Absence of Formal Tax Compliance**: Inability to generate compliant GST invoices (HSN 8548/8549) locks collectors out of formal supply chains.
4. **Literacy & Vernacular Language Barriers**: Complex enterprise software excludes grassroot collectors fluent only in Hindi or Marathi.
5. **Zero Traceability for CPCB / EPR**: Formal recyclers cannot prove legal chain-of-custody to the Central Pollution Control Board (CPCB) for Extended Producer Responsibility (EPR) credits.

**EcoBridge transforms informal collectors into certified, formalized micro-entrepreneurs** through an integrated 4-tier platform.

---

## 2. System Architecture & Component Overview

```text
                               +--------------------------------------------+
                               |        Informal Collector Android App      |
                               |   - On-Device MobileNetV2 (TFLite 2.16.1)  |
                               |   - Room Offline SQLite + WorkManager Sync |
                               |   - Marathi / Hindi / English Voice Audio  |
                               |   - 5% Reverse GST + Denomination Counter  |
                               +---------------------+----------------------+
                                                     |
                                        Delta Sync / Photo Hash (SHA-256)
                                                     v
                               +---------------------+----------------------+
                               |      FastAPI Async Backend Services        |
                               |   - Alembic Managed SQLite / PostgreSQL    |
                               |   - Atomic Custody Transition Pipeline     |
                               |   - Market Benchmark Pricing Engine        |
                               |   - Demo Safety Gating (DEMO_MODE flag)    |
                               +----------+----------------------+----------+
                                          |                      |
                    Verified Custody Chain|                      |Audit Manifests
                                          v                      v
            +-----------------------------+------+   +-----------+--------------------------+
            |    Certified Recycler Portal       |   |   CPCB Regulator & Admin Dashboard   |
            |   - Next.js 14 / Tailwind CSS      |   |   - Next.js 14 / Tailwind CSS        |
            |   - Live Scrap Marketplace         |   |   - Municipal Flow Heatmaps          |
            |   - Gross/Tare Weighbridge Audit   |   |   - DPDP Act Compliance Registry     |
            |   - Form-6 CPCB Manifest Exporter  |   |   - EPR Green Dividend Tracking      |
            +------------------------------------+   +--------------------------------------+
```

---

## 3. Key Platform Capabilities

### 🤖 1. On-Device Edge AI Classifier (TFLite 2.16.1)
- **Zero-Latency Offline Inference**: Deployed `mobilenet_scrap_v1.tflite` model (2.5 MB) inside Android assets; runs in <150ms without internet.
- **Async Pre-Warming**: `EcoBridgeApplication` pre-warms the neural network singleton on startup, preventing camera preview freeze.
- **8 Scrap Taxonomies**: CRT TVs/Monitors (Hazardous), LCD/LED Panels, Printed Circuit Boards (PCBs), Copper Cables, Batteries (Hazardous), Motors & Magnets, Mixed Plastics, Other Scrap.
- **Safety Hazards Before Prices**: Mandates safety warnings (swollen lithium fire hazard, leaded glass PPE, acid inhalation) **before** rendering financial estimates.

### ⛓️ 2. Tamper-Evident Cryptographic Chain of Custody
- Every lot transition creates an unbroken SHA-256 block linking:
  `SHA-256(LOT_UUID | RECYCLER_ID | WEIGHBRIDGE_NET | TAX_INVOICE | PREVIOUS_EVENT_HASH | TIMESTAMP)`
- Transitions (`OFFER_ACCEPTED`, `PHYSICAL_HANDOVER`, `HANDOVER_CONFIRMED`, `PAYMENT_SETTLED`) are wrapped in **atomic database transactions** ensuring no status update occurs without its signed audit event.
- Statutory **Form-6 CPCB E-Waste Manifest** is generated with cryptographic verification.

### 🗣️ 3. Vernacular Audio & Voice-First Accessibility
- **Trilingual Parity**: 100% string and audio parity across Marathi (मराठी), Hindi (हिन्दी), and English.
- **Dual-Mode Audio Pipeline**:
  - High-fidelity studio recordings (`.ogg`) in `collector_app/app/src/main/res/raw/`.
  - Android TTS fallback configured at `0.95x` speech rate for noisy scrap-yard environments.
- **Language Switcher**: Dedicated settings activity with zero-restart context wrapping.

### 💵 4. Indian GST (5%) & Physical Cash Denomination Counter
- Computes 5% Reverse Charge GST (2.5% CGST + 2.5% SGST) under HSN 8548/8549.
- Generates statutory Indian tax invoice format (`TXI-YYYY-STATE-XXXXXX`).
- Physical scrap yards operate on cash: live denomination counter (₹500, ₹200, ₹100, ₹50, ₹20, ₹10, ₹5, coins) with greedy auto-fill change algorithm and live match badges.

### 🛡️ 5. DPDP Act (2023) Compliance & Security
- **Data Minimization**: Zero storage of Aadhaar numbers, biometric face data, contacts, or SMS logs.
- **Vernacular Audio Consent**: Plain-language consent audio playback before scrap registration.
- **Child Labor Safeguard**: Mandatory 18+ age verification check.
- **Hardened Auth**: Demo OTP (`123456`) and `/demo-login` strictly blocked in production (`DEMO_MODE=false`).

---

## 4. Repository Structure

```text
Ecobridge-repo/
├── collector_app/               # Native Android Client (Java 17, Room, WorkManager, TFLite 2.16.1)
│   ├── app/src/main/assets/     # mobilenet_scrap_v1.tflite neural network
│   ├── app/src/main/java/       # MVVM, Room DB, AI Safety Analyzer, Sync Engine
│   └── app/src/main/res/        # Vernacular strings (values, values-hi, values-mr)
├── release/                     # Pre-compiled production artifacts
│   └── EcoBridge-Collector-v1.0.apk # Standalone installable Android APK (29.4 MB)
├── backend/                     # FastAPI Async Microservice (Python 3.11+)
│   ├── src/api/v1/endpoints/    # lots, sync, recycler_portal, pricing, auth
│   ├── src/models/              # SQLAlchemy Async Models (User, Lot, CustodyEvent)
│   ├── src/services/            # CustodyService, LotService, OTPService
│   ├── alembic/                 # Alembic migration revisions (b9c2401a0dfe)
│   └── tests/                   # Pytest automated test suite (21 tests)
├── recycler_portal/             # Certified Recycler Web App (Next.js 14 App Router)
├── admin_dashboard/             # CPCB Regulator & Admin Portal (Next.js 14 App Router)
├── packages/                    # Monorepo shared packages
│   ├── api-contracts/           # Shared TypeScript types and Zod schemas
│   ├── crypto-traceability/     # SHA-256 chain-of-custody utilities
│   ├── ui/                      # Shared Tailwind UI components
│   └── i18n/                    # Multilingual translation dictionaries
├── docs/                        # SIH 2026 Strategy Playbook & Defense Guides
├── scripts/                     # Automated end-to-end integration test runners
├── DEPLOY.md                    # Free cloud deployment guide (Render + Vercel)
└── HANDOVER.md                  # Comprehensive engineering assessment & audit
```

---

## 5. Quick Start & Local Execution

### Prerequisites
- Python 3.11+
- Node.js 18+ & `pnpm` (>= 9) or `npm`
- Java 17 & Android Studio (optional, to rebuild APK)

---

### Step 1: Run Backend API Server
```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload
```
Interactive API docs: `http://127.0.0.1:8000/docs`

---

### Step 2: Run Certified Recycler Portal
```powershell
cd recycler_portal
npm install
npm run dev
```
Open `http://localhost:3000` (or `3001`). Click **Demo Recycler Login** (`+919811111111` / `123456`).

---

### Step 3: Run CPCB Regulator & Admin Dashboard
```powershell
cd admin_dashboard
npm install
npm run dev
```
Open `http://localhost:3002`. Inspect real-time scrap collection heatmaps, DPDP registries, and pricing benchmarks.

---

### Step 4: Install Android Collector App
Directly install the pre-compiled APK on an Android device or emulator:
```powershell
adb install release\EcoBridge-Collector-v1.0.apk
```
*Or rebuild from source:*
```powershell
cd collector_app
.\gradlew.bat assembleDebug
```

---

## 6. Testing & Quality Assurance

Every layer of the platform is validated by automated test suites:

### 1. Backend Pytest Suite (21 / 21 Tests Passing)
```powershell
cd backend
.\venv\Scripts\pytest.exe -v
```
```text
======================== 21 passed, 1 warning in 2.78s ========================
- test_settings_default                         PASSED
- test_taxonomy_materials_endpoint              PASSED
- test_native_collector_batch_is_idempotent     PASSED
- test_get_all_benchmark_prices                 PASSED
- test_complete_recycler_journey                PASSED
- test_custody_events_unavoidable_on_transitions PASSED
- test_demo_auth_gating_when_disabled           PASSED
...
```

### 2. Recycler Web Portal Production Build
```powershell
cd recycler_portal
npm run build
# Result: Compiled successfully (12/12 routes static/dynamic optimized)
```

### 3. Admin Dashboard Production Build
```powershell
cd admin_dashboard
npm run build
# Result: Compiled successfully (10/10 routes static optimized)
```

### 4. Android Native Gradle Build
```powershell
cd collector_app
.\gradlew.bat assembleDebug
# Result: BUILD SUCCESSFUL in 15s -> EcoBridge-Collector-v1.0.apk (29.4 MB)
```

---

## 7. Cloud Deployment (Render & Vercel)

The repository includes ready-to-deploy configurations for **100% free hosting**:
- **Backend (Render Blueprint)**: `render.yaml` automatically installs dependencies, executes `alembic upgrade head`, and starts Uvicorn.
- **Portals (Vercel)**: Zero-configuration Next.js deployment for both `recycler_portal` and `admin_dashboard`.
- **Step-by-step instructions**: Refer to [`DEPLOY.md`](DEPLOY.md).

---

## 8. SIH 2026 Evaluation Walkthrough Script (5 Minutes)

1. **Step 1: Offline Lot Creation (Android App)**
   - Open EcoBridge Collector app.
   - Tap **"Weigh New Scrap"** -> Snap photo of e-waste scrap.
   - AI classifies item as *Battery / CRT / PCB* -> App alerts on mandatory PPE / safety precautions.
   - Enter weight (e.g. `12.5 kg`) -> App calculates benchmark price & 5% GST invoice.
   - Tap **Save Offline** -> Persisted immediately in on-device SQLite Room DB.

2. **Step 2: Delta Sync & Custody Hash**
   - Tap **Sync Now** (or auto-triggers when network resumes).
   - WorkManager uploads batch with SHA-256 integrity hash to FastAPI backend.

3. **Step 3: Recycler Acceptance & Weighbridge Audit**
   - Log into Recycler Portal (`+919811111111` / `123456`).
   - Browse **Materials Marketplace** -> Select incoming collector lot.
   - Accept offer -> Record weighbridge gross/tare measurement.
   - Confirm handover -> Disburse settlement.

4. **Step 4: Tamper-Evident Ledger & CPCB Manifest**
   - Navigate to **Ledger** -> Inspect unbroken chain of custody with actor signatures and SHA-256 blocks.
   - Export statutory **Form-6 CPCB Manifest** for official EPR credit filing.

5. **Step 5: Regulator Oversite (Admin Dashboard)**
   - Open Admin Dashboard -> Review city-wide collection heatmaps and DPDP compliance audits.

---

## 9. Contributors & License

Developed with ❤️ for **Smart India Hackathon 2026** (Problem Statement 26229: *Kabadiwala Connect*).

Licensed under the [MIT License](LICENSE).
