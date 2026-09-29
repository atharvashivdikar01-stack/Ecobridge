# ECOBRIDGE (कबाड़ीवाला कनेक्ट)
### Formalizing India's Informal E-Waste Economy with Edge AI & Tamper-Evident Traceability

[![SIH 2026](https://img.shields.io/badge/SIH%202026-Problem%20Statement%2026229-16a34a?style=for-the-badge)](https://sih.gov.in)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI%20Async-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js 14](https://img.shields.io/badge/Web%20Portals-Next.js%2014-000000?style=for-the-badge&logo=next.js&logoColor=white)](https://nextjs.org)
[![Android](https://img.shields.io/badge/Mobile-Android%20Java%2017-3DDC84?style=for-the-badge&logo=android&logoColor=white)](https://developer.android.com)
[![TensorFlow Lite](https://img.shields.io/badge/Edge%20AI-TFLite%202.16.1-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white)](https://tensorflow.org/lite)
[![DPDP Act 2023](https://img.shields.io/badge/Compliance-DPDP%20Act%202023-blue?style=for-the-badge)](https://www.meity.gov.in)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

---

## 🏆 Quick Evaluation Hub (For Hackathon Judges)

| Component | Access Link / Asset | Demo Credentials |
|---|---|---|
| **Certified Recycler Operations Portal** | [`ecobridge-recycler-portal.vercel.app`](https://ecobridge-recycler-portal.vercel.app) *(or `localhost:3000`)* | Phone: `+919811111111`<br>OTP: `123456` |
| **CPCB Regulator & Platform Dashboard** | [`ecobridge-admin-dashboard.vercel.app`](https://ecobridge-admin-dashboard.vercel.app) *(or `localhost:3002`)* | Instant 1-Click Role Switcher |
| **Interactive Backend OpenAPI Specs** | [`ecobridge-api-sih26.azurewebsites.net/docs`](https://ecobridge-api-sih26-d3hfbccrg3fpddcr.centralindia-01.azurewebsites.net/docs) *(or `localhost:8000/docs`)* | Interactive Swagger UI |
| **Pre-Built Collector Android APK (v1.1)** | [📥 **Download `release/EcoBridge-Collector-v1.1.apk`**](release/EcoBridge-Collector-v1.1.apk) | Direct install on Android 8.0+ (25.3 MB) — connects to Azure auto |
| **Full Cloud Deployment Guide** | [📖 **`docs/DEPLOYMENT.md`**](docs/DEPLOYMENT.md) | Complete step-by-step setup guide |

---

## 1. Executive Summary & Mission

Over **90% of India's electronic waste** is processed by the informal recycling sector—over **1.5 million waste pickers, scrap aggregators, and neighborhood *kabadiwalas***. Despite recovering precious urban mining materials, informal collectors operate in dangerous, opaque conditions:

```
    INFORMAL REALITY (Today)                  ECOBRIDGE DIGITAL HIGHWAY
 ❌ Predatory middleman price cuts       ==>   ✅ Real-time benchmark pricing bands
 ❌ Toxic acid leaching & battery fires  ==>   ✅ Mandatory AI safety & PPE hazard alerts
 ❌ Zero tax compliance / no GST         ==>   ✅ Automated 5% Reverse GST (HSN 8548/8549)
 ❌ Illiteracy & vernacular barriers     ==>   ✅ Marathi/Hindi/English voice audio guidance
 ❌ Fake EPR claims & illegal dumping    ==>   ✅ Tamper-evident SHA-256 chain of custody
```

**EcoBridge transforms informal waste pickers into formalized, protected, digitally-settled micro-entrepreneurs** through an offline-first mobile app connected to CPCB-certified recyclers.

---

## 2. System Architecture

```text
 ┌────────────────────────────────────────────────────────────────────────┐
 │                   INFORMAL COLLECTOR ANDROID CLIENT                    │
 │  • On-Device TFLite 2.16.1 Vision Classifier (<150ms offline inference)│
 │  • Room SQLite Offline Store + WorkManager Background Queue            │
 │  • Marathi / Hindi / English Voice Engine (Human .ogg + TTS fallback)  │
 │  • Indian 5% Reverse GST Engine + Cash Denomination Counter            │
 └───────────────────────────────────┬────────────────────────────────────┘
                                     │
                    Background Delta Sync / SHA-256 Hash
                                     ▼
 ┌────────────────────────────────────────────────────────────────────────┐
 │                     FASTAPI ASYNC BACKEND SERVICES                     │
 │  • Alembic Schema Migrations (SQLite / PostgreSQL with PostGIS)        │
 │  • Atomic Custody Event Pipeline (Unbroken SHA-256 State Transitions)  │
 │  • Real-Time Market Benchmark Pricing & Tax Invoicing Engine           │
 │  • Enterprise Security (DEMO_MODE safety flags, DPDP data minimization)│
 └─────────────────────┬────────────────────────────┬─────────────────────┘
                       │                            │
     Cryptographic Chain of Custody         Statutory Audit Trail
                       ▼                            ▼
 ┌───────────────────────────────────┐  ┌───────────────────────────────────┐
 │     CERTIFIED RECYCLER PORTAL     │  │   CPCB REGULATOR & ADMIN PORTAL   │
 │ • Next.js 14 App Router + Tailwind│  │ • Next.js 14 App Router + Tailwind│
 │ • Real-Time Scrap Marketplace     │  │ • Municipal E-Waste Flow Heatmap  │
 │ • Weighbridge Gross/Tare Audit    │  │ • DPDP Compliance Registry        │
 │ • Form-6 CPCB Manifest Exporter   │  │ • Extended Producer Responsibility│
 └───────────────────────────────────┘  └───────────────────────────────────┘
```

---

## 3. Deep-Tech Innovations

### 🤖 1. On-Device Edge AI Vision Classifier (TFLite 2.16.1)
- **Zero-Latency Offline Inference:** Custom-quantized MobileNetV2 (`mobilenet_scrap_v1.tflite`, 2.5 MB) packaged directly into Android assets. Runs in **sub-150ms** without internet access.
- **Async Neural Pre-Warming:** Pre-warms model tensors in a background thread during application boot, eliminating camera preview freeze.
- **Safety Hazards Before Prices:** Mandatory hazard alerts (swollen lithium battery fire risk, leaded CRT glass, toxic PCB fumes) display **before** any financial valuation.

### ⛓️ 2. Tamper-Evident SHA-256 Chain of Custody
- Every batch transition computes an immutable cryptographic digest:
  $$\text{Hash} = \text{SHA-256}(\text{LotUUID} \parallel \text{RecyclerID} \parallel \text{NetWeight} \parallel \text{TaxInvoice} \parallel \text{PrevHash} \parallel \text{Timestamp})$$
- Status transitions (`OFFER_ACCEPTED`, `PHYSICAL_HANDOVER`, `HANDOVER_CONFIRMED`, `PAYMENT_SETTLED`) execute in **atomic database transactions** ensuring no status update occurs without a signed custody event.
- Generates statutory **Form-6 CPCB E-Waste Manifests** with cryptographic verification.

### 🗣️ 3. Vernacular Audio & Voice-First UX
- **100% Trilingual Parity:** Seamless context switching across Marathi (मराठी), Hindi (हिन्दी), and English without app restart.
- **Dual-Mode Voice Pipeline:** High-fidelity human voice recordings (`.ogg`) in `res/raw/` with automatic Android TTS fallback tuned at `0.95x` rate for noisy scrap-yard environments.

### 💵 4. Indian 5% Reverse GST & Physical Cash Denomination Counter
- Automatic 5% GST computation (2.5% CGST + 2.5% SGST) under HSN 8548/8549 with statutory invoice numbering (`TXI-YYYY-STATE-XXXXXX`).
- Physical cash note counter (₹500, ₹200, ₹100, ₹50, ₹20, ₹10, coins) featuring a greedy change algorithm and live match badges.

### 🛡️ 5. DPDP Act (2023) Compliance & Privacy Architecture
- **Data Minimization:** Zero storage of Aadhaar numbers, biometric data, contacts, or SMS logs.
- **Vernacular Audio Consent:** Audio-visual plain-language consent notice before first scrap collection.
- **Child Labor Safeguards:** Mandatory age declaration ($\ge 18$) to prevent child labor in informal recycling.

---

## 4. Repository Structure

```text
Ecobridge-repo/
├── .github/workflows/           # CI/CD: Automated backend, frontend & dataset tests
├── admin_dashboard/             # Next.js 14 CPCB Regulator & Admin Portal
├── ai/                          # Training pipelines, notebooks & TFLite quantization
├── backend/                     # FastAPI async backend microservices & Alembic migrations
├── collector_app/               # Native Android App (Java 17, Room, WorkManager, TFLite)
├── datasets/                    # Synthetic validation datasets & schema verification
├── docs/                        # Complete architecture, deployment & SIH guides
│   ├── ARCHITECTURE.md          # Domain architectures & data flows
│   ├── DEPLOYMENT.md            # Free hosting guide (Render + Vercel)
│   ├── ROADMAP.md               # Feature roadmap & task tracking
│   └── EcoBridge_SIH_Winning_PPT_Strategy_and_Guide.docx
├── infra/                       # Docker, Kubernetes & Terraform deployment templates
├── packages/                    # Monorepo TypeScript libraries
│   ├── api-contracts/           # Shared Zod schemas & DTO types
│   ├── crypto-traceability/     # SHA-256 chain-of-custody utilities
│   ├── ui/                      # Shared Tailwind UI components
│   └── i18n/                    # Multilingual translation dictionaries
├── recycler_portal/             # Next.js 14 Certified Recycler Portal
├── release/                     # Production binary distribution
│   └── EcoBridge-Collector-v1.0.apk # Pre-compiled installable Android APK (29.4 MB)
├── scripts/                     # Automated end-to-end integration test runners
├── LICENSE                      # MIT License
├── package.json                 # Monorepo scripts (Turborepo + pnpm)
├── README.md                    # Flagship project showcase
└── render.yaml                  # 1-Click Render Cloud deployment blueprint
```

---

## 5. Local Setup & Quick Start

### Prerequisites
- **Python 3.11+**
- **Node.js 18+** & `pnpm` (>= 9) or `npm`
- **Android SDK 34 / JDK 17** *(only needed to rebuild Android APK)*

---

### Step 1: Start Backend API
```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload
```
Interactive Swagger API docs: `http://127.0.0.1:8000/docs`

---

### Step 2: Start Recycler Operations Portal
```powershell
cd recycler_portal
npm install
npm run dev
```
Open `http://localhost:3000` (or `3001`). Use 1-Click Recycler Demo Login (`+919811111111` / `123456`).

---

### Step 3: Start CPCB Regulator Dashboard
```powershell
cd admin_dashboard
npm install
npm run dev
```
Open `http://localhost:3002`. Inspect real-time scrap flows, municipal heatmaps, and DPDP compliance audits.

---

### Step 4: Install Android Collector App
Sideload the pre-built APK directly onto an Android device or emulator:
```powershell
adb install release\EcoBridge-Collector-v1.0.apk
```

---

## 6. Automated Testing & Quality Assurance

All platform components are verified by automated testing:

| Test Suite | Command | Result |
|---|---|---|
| **Backend Pytest** | `pytest backend/tests -v` | **21 / 21 Tests Passed** (2.8s) |
| **Recycler Portal Build** | `pnpm --filter @ecobridge/recycler-portal build` | **Compiled & Optimized (12 routes)** |
| **Admin Dashboard Build** | `pnpm --filter @ecobridge/admin-dashboard build` | **Compiled & Optimized (10 routes)** |
| **Monorepo Linting** | `pnpm lint` | **Zero Lint Errors (5/5 tasks passed)** |
| **Dataset Validation** | `python datasets/scripts/validate_datasets.py` | **All 8 Datasets Validated** |
| **Android APK Build** | `./gradlew assembleDebug` | **Build Successful (29.4 MB APK)** |

---

## 7. 5-Minute Judge Demo Walkthrough

1. **Step 1: Offline Lot Creation (Android App)**
   - Open EcoBridge Collector app.
   - Tap **"Weigh New Scrap"** ➔ Take scrap photo.
   - Edge AI detects *Battery / CRT / PCB* ➔ App displays mandatory PPE/safety warnings.
   - Enter scale weight (e.g. `15.0 kg`) ➔ Benchmark price and 5% GST calculated.
   - Tap **Save Offline** ➔ Staged in local SQLite Room database without internet.

2. **Step 2: WorkManager Delta Sync**
   - Tap **Sync Now** (or auto-triggers when internet reconnects).
   - Lot metadata and photo SHA-256 hash sync to the FastAPI backend.

3. **Step 3: Recycler Acceptance & Weighbridge Audit (Web Portal)**
   - Open Recycler Portal ➔ Log in with `+919811111111` / `123456`.
   - Materials Marketplace ➔ Accept collector scrap batch.
   - Confirm weighbridge gross and tare scale reading ➔ Settle payment.

4. **Step 4: Tamper-Evident Ledger & Form-6 CPCB Manifest**
   - View **Ledger** ➔ Inspect unbroken SHA-256 chain of custody with digital signatures.
   - Download statutory **Form-6 CPCB Manifest** for official EPR credit filing.

5. **Step 5: Regulator Oversite (Admin Dashboard)**
   - Open Admin Dashboard ➔ Review city-wide collection heatmaps and DPDP compliance audits.

---

## 8. Documentation Index

- 📐 [**System Architecture & Domain Design**](docs/ARCHITECTURE.md)
- 🚀 [**Zero-Cost Cloud Deployment Guide (Render + Vercel)**](docs/DEPLOYMENT.md)
- 🗺️ [**Engineering Roadmap & Task Register**](docs/ROADMAP.md)
- 💻 [**Local Development Guidelines**](docs/DEVELOPMENT.md)

---

## 9. Contributors & License

Developed with ❤️ for **Smart India Hackathon 2026** (Problem Statement 26229: *Kabadiwala Connect*).

Licensed under the [MIT License](LICENSE).
