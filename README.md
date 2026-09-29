# ECOBRIDGE (कबाड़ीवाला कनेक्ट)
### Formalizing India's Informal E-Waste Economy with Edge AI, Vernacular Voice UX & Tamper-Evident Traceability

[![SIH 2026](https://img.shields.io/badge/SIH%202026-Problem%20Statement%2026229-16a34a?style=for-the-badge)](https://sih.gov.in)
[![Backend Live](https://img.shields.io/badge/Azure%20Cloud-FastAPI%20Live-0078D4?style=for-the-badge&logo=microsoftazure&logoColor=white)](https://ecobridge-api-sih26-d3hfbccrg3fpddcr.centralindia-01.azurewebsites.net/docs)
[![Recycler Portal](https://img.shields.io/badge/Vercel-Recycler%20Portal-000000?style=for-the-badge&logo=vercel&logoColor=white)](https://ecobridge-recycler-portal.vercel.app)
[![Admin Portal](https://img.shields.io/badge/Vercel-Regulator%20Dashboard-000000?style=for-the-badge&logo=vercel&logoColor=white)](https://ecobridge-admin-dashboard.vercel.app)
[![Android APK](https://img.shields.io/badge/Android%20v1.2-APK%20Download-3DDC84?style=for-the-badge&logo=android&logoColor=white)](https://github.com/atharvashivdikar01-stack/Ecobridge/raw/main/release/EcoBridge-Collector-v1.2.apk)
[![Edge AI](https://img.shields.io/badge/Edge%20AI-TFLite%202.16.1-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white)](https://tensorflow.org/lite)
[![Compliance](https://img.shields.io/badge/Compliance-DPDP%20Act%202023-blue?style=for-the-badge)](https://www.meity.gov.in)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

---

## 🏆 Quick Evaluation Hub (For Hackathon Judges)

All production environments, cloud microservices, and mobile binaries are live and fully operational:

| Platform Component | Live Link / Download | Demo Credentials / Access |
|---|---|---|
| **Certified Recycler Operations Portal** | [🔗 `ecobridge-recycler-portal.vercel.app`](https://ecobridge-recycler-portal.vercel.app) | **1-Click Demo Login** or:<br>Phone: `+919811111111` \| OTP: `123456` |
| **CPCB Regulator & Platform Admin** | [🔗 `ecobridge-admin-dashboard.vercel.app`](https://ecobridge-admin-dashboard.vercel.app) | **1-Click Instant Role Switcher**<br>*(Regulator / Platform Admin)* |
| **Live Azure Cloud API & Swagger Docs** | [🔗 `ecobridge-api-sih26.azurewebsites.net/docs`](https://ecobridge-api-sih26-d3hfbccrg3fpddcr.centralindia-01.azurewebsites.net/docs) | Interactive Swagger UI (35+ Endpoints) |
| **Azure Backend Health Status** | [🔗 `ecobridge-api-sih26.azurewebsites.net/api/v1/health`](https://ecobridge-api-sih26-d3hfbccrg3fpddcr.centralindia-01.azurewebsites.net/api/v1/health) | `{"status": "ok", "database": "connected"}` |
| **Collector Android APK (v1.2.0 - Latest)** | [📥 **Download `EcoBridge-Collector-v1.2.apk`**](https://github.com/atharvashivdikar01-stack/Ecobridge/raw/main/release/EcoBridge-Collector-v1.2.apk) | **1-Click Online Login (Raju Shinde)**,<br>OTP: `+919800000001` / `123456`, or **Offline** |
| **GitHub Release Package (v1.2.0)** | [📦 **GitHub Tag v1.2.0 Release**](https://github.com/atharvashivdikar01-stack/Ecobridge/releases/tag/v1.2.0) | Complete release binary & assets |
| **Complete Deployment Guide** | [📖 `docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md) | Azure + Vercel deployment walkthrough |

---

## 1. Executive Summary & Mission

Over **90% of India's electronic waste** is processed by the informal sector—encompassing over **1.5 million waste pickers, scrap aggregators, and neighborhood *kabadiwalas***. Despite recovering critical urban mining materials (copper, gold, rare-earths), informal collectors operate in dangerous, financially exploited, and opaque conditions:

```
    INFORMAL REALITY (Today)                  ECOBRIDGE DIGITAL HIGHWAY
 ❌ Predatory middleman price cuts       ==>   ✅ Real-time benchmark pricing bands
 ❌ Toxic acid leaching & battery fires  ==>   ✅ Mandatory AI safety & PPE hazard alerts
 ❌ Zero tax compliance / no GST         ==>   ✅ Automated 5% Reverse GST (HSN 8548/8549)
 ❌ Illiteracy & vernacular barriers     ==>   ✅ Marathi/Hindi/English voice audio guidance
 ❌ Fake EPR claims & illegal dumping    ==>   ✅ Tamper-evident SHA-256 chain of custody
```

**EcoBridge transforms informal waste pickers into formalized, protected, digitally-settled micro-entrepreneurs** through an offline-first mobile app connected directly to CPCB-certified recycling facilities.

---

## 2. System Architecture

```text
 ┌────────────────────────────────────────────────────────────────────────┐
 │                   INFORMAL COLLECTOR ANDROID CLIENT                    │
 │  • On-Device TFLite 2.16.1 Vision Classifier (<150ms offline inference)│
 │  • Room SQLite Offline Store + WorkManager Background Queue            │
 │  • Marathi / Hindi / English Voice Engine (Human .ogg + TTS fallback)  │
 │  • Indian 5% Reverse GST Engine + Cash Denomination Counter            │
 │  • 1-Click Online Cloud Authentication + Zero-Data-Loss Offline Fallback│
 └───────────────────────────────────┬────────────────────────────────────┘
                                     │
                    Background Delta Sync / SHA-256 Hash
                                     ▼
 ┌────────────────────────────────────────────────────────────────────────┐
 │               FASTAPI ASYNC BACKEND (Microsoft Azure Cloud)            │
 │  • PostgreSQL 16 with PostGIS Geospatial Extension                     │
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
│   ├── src/api/v1/endpoints/    # REST endpoints (auth, lots, sync, prices, recyclers, analytics)
│   ├── src/core/                # Config, database engine, security
│   ├── src/models/              # SQLAlchemy ORM models
│   └── tests/                   # Pytest test suite (21 automated tests)
├── collector_app/               # Native Android App (Java 17, Room, WorkManager, TFLite)
│   ├── app/src/main/java/       # Architecture components (Room, Retrofit, AudioPrompt, UI)
│   └── app/src/main/res/        # Layouts, themes, vernacular strings (en, hi, mr)
├── datasets/                    # Synthetic validation datasets & schema verification
├── docs/                        # Complete architecture, deployment & SIH guides
│   ├── ARCHITECTURE.md          # Domain architectures & data flows
│   ├── DEPLOYMENT.md            # Cloud hosting guide (Azure + Vercel)
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
│   ├── EcoBridge-Collector-v1.2.apk      # Latest release APK (Cloud-connected + 1-Click login)
│   └── EcoBridge-Collector-latest.apk    # Symlink copy of latest build
├── LICENSE                      # MIT License
├── package.json                 # Monorepo scripts (Turborepo + pnpm)
└── README.md                    # Flagship project showcase
```

---

## 5. Live Testing & Judge Demo Walkthrough

### 🚀 Quick Evaluation Walkthrough (5 Minutes):

1. **Step 1: Open the Collector Android App**
   - Download and install [**`EcoBridge-Collector-v1.2.apk`**](https://github.com/atharvashivdikar01-stack/Ecobridge/raw/main/release/EcoBridge-Collector-v1.2.apk).
   - On the login screen, tap **`⚡ 1-Click Online Login (Raju Shinde)`** *(or log in with `+919800000001` / `123456`, or tap `Continue Offline`)*.
   - The app instantly authenticates against the live Azure backend and opens the home dashboard in **ONLINE** status.

2. **Step 2: Create a Scrap Lot (Works Online or 100% Offline)**
   - Tap **"Weigh New Scrap"** ➔ Select material (e.g. *Batteries* or *CRT Glass*).
   - The on-device Edge AI classifies scrap and immediately displays PPE/Safety Warnings before valuation.
   - Enter approximate weight (e.g. `12.5 kg`) ➔ Real-time benchmark pricing and statutory 5% reverse GST are auto-calculated.
   - Save the lot ➔ A unique QR token is generated and persisted locally in SQLite Room DB.

3. **Step 3: Background WorkManager Cloud Sync**
   - If offline, records are held securely on the phone.
   - Once connected, the app performs delta-sync with the Azure backend (`/api/v1/sync/batch`), posting the lot metadata and SHA-256 evidence hash.

4. **Step 4: Recycler Acceptance & Settlement (Web Portal)**
   - Open the [**Certified Recycler Operations Portal**](https://ecobridge-recycler-portal.vercel.app).
   - Click **`⚡ Demo Recycler Login (Apex CleanTech Recyclers)`** *(or `+919811111111` / `123456`)*.
   - Navigate to **Materials Marketplace** ➔ Locate the synced lot.
   - Click **Accept Offer** ➔ Record weighbridge gross/tare measurements.
   - Settle payment via UPI or Cash ➔ Chain of custody registers the transaction with SHA-256 digital signatures.

5. **Step 5: Inspect Form-6 Manifest & Regulator Dashboard**
   - In Recycler Portal, open **Ledger** ➔ Download the statutory **CPCB Form-6 E-Waste Manifest**.
   - Open the [**CPCB Regulator Dashboard**](https://ecobridge-admin-dashboard.vercel.app) to inspect municipal collection heatmaps, EPR credit fulfillment, and DPDP compliance audits.

---

## 6. Automated Testing & Verification

All platform components are verified by automated testing:

| Test Suite | Command | Result |
|---|---|---|
| **Backend Pytest Suite** | `pytest backend/tests -v` | **21 / 21 Tests Passed** (2.8s) |
| **Live Azure API Endpoints** | Integration Script | **11 / 11 Endpoints Verified (200 OK)** |
| **Recycler Portal Build** | `pnpm --filter @ecobridge/recycler-portal build` | **Compiled & Optimized (12 routes)** |
| **Admin Dashboard Build** | `pnpm --filter @ecobridge/admin-dashboard build` | **Compiled & Optimized (10 routes)** |
| **Monorepo Linting** | `pnpm lint` | **Zero Lint Errors (5/5 tasks passed)** |
| **Dataset Validation** | `python datasets/scripts/validate_datasets.py` | **All 8 Datasets Validated** |
| **Android APK Build** | `./gradlew assembleDebug` | **Build Successful (`EcoBridge-Collector-v1.2.apk`)** |

---

## 7. Local Setup Instructions

### Prerequisites
- **Python 3.11+**
- **Node.js 18+** & `pnpm` (>= 9) or `npm`
- **Android SDK 34 / JDK 17** *(only needed if recompiling the Android APK from source)*

```powershell
# 1. Clone repository
git clone https://github.com/atharvashivdikar01-stack/Ecobridge.git
cd Ecobridge

# 2. Run Backend API
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload

# 3. Run Recycler Portal (in a separate terminal)
cd recycler_portal
npm install
npm run dev

# 4. Run CPCB Regulator Dashboard (in a separate terminal)
cd admin_dashboard
npm install
npm run dev

# 5. Sideload Collector Android APK
adb install release\EcoBridge-Collector-v1.2.apk
```

---

## 8. Documentation Index

- 📐 [**System Architecture & Domain Design**](docs/ARCHITECTURE.md)
- 🚀 [**Zero-Cost Cloud Deployment Guide (Azure + Vercel)**](docs/DEPLOYMENT.md)
- 🗺️ [**Engineering Roadmap & Task Register**](docs/ROADMAP.md)
- 📱 [**Android Application Specification**](docs/ANDROID_APP.md)

---

## 9. Contributors & License

Developed with ❤️ for **Smart India Hackathon 2026** (Problem Statement 26229: *Kabadiwala Connect*).

Licensed under the [MIT License](LICENSE).
