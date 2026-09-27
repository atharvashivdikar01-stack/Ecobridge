# ECOBRIDGE — Master Architecture & Project Context

> **Target Audience:** AI Coding Assistants, Human Engineers, and Evaluators.  
> **Problem Statement:** SIH 2026 Problem Statement 26229 — *Kabadiwala Connect* (Formalizing the Informal E-Waste Supply Chain).  
> **Repository:** `atharvashivdikar01-stack/Ecobridge`  
> **Last Updated:** September 2026  

---

## 1. Executive Summary & Mission

### The Real-World Problem
In emerging economies (particularly India), over **90% of electronic waste (e-waste)** is collected and dismantled by the **informal sector** (*kabadiwalas*, waste pickers, local scrap aggregators). These informal workers:
- Lack scientific tools to identify hazardous materials (e.g., toxic CRT lead, lithium battery fires, mercury switches).
- Face price exploitation from predatory middlemen due to opaque market rates.
- Have no verifiable proof of custody to participate in formal **Extended Producer Responsibility (EPR)** carbon/recycling credit markets.

### The EcoBridge Solution
EcoBridge is an end-to-end digital bridge connecting informal collectors directly to government-certified, formal e-waste recyclers:
1. **Offline-First Collector Android App:** Empowers low-literacy collectors with vernacular voice prompts (Hindi, Marathi, English), camera-guided scrap classification, and offline lot staging without requiring constant internet.
2. **On-Device AI Classification & Hazard Warning:** Uses computer vision to identify scrap categories (PCBs, Batteries, Cables, CRT, etc.) and immediately enforces safety/PPE warnings before generating fair price estimates.
3. **Cryptographic Chain of Custody:** Generates tamper-evident SHA-256 hashed custody transfer records with QR codes and photo audit trails for verified EPR traceability.
4. **Recycler Web Portal:** A Next.js web application for certified recycling facilities to discover aggregated lots, confirm physical handovers, verify weights, and log transparent payouts.

---

## 2. Total Technology Stack

| Layer | Technologies & Frameworks | Key Responsibilities |
|---|---|---|
| **Mobile Client (`collector_app`)** | Native Android (Java 17 / Gradle 8.2), Room Database, WorkManager, CameraX, TensorFlow Lite, Android TTS & local OGG audio | Offline-first data capture, photo hashing, on-device AI inference, vernacular audio feedback, background sync queue. |
| **Backend API (`backend`)** | Python 3.11+, FastAPI, SQLAlchemy 2.0 (Async), Pydantic v2, Uvicorn, Passlib/JWT, SQLite (local) / PostgreSQL (production) | RESTful API, offline delta sync protocol, dynamic pricing bands, auto-bootstrap catalog, SHA-256 custody ledger, payment settlement. |
| **Recycler Portal (`recycler_portal`)** | Next.js 14 (App Router), React 18, TypeScript, Tailwind CSS, Next rewrites proxy | Recycler authentication, live lot marketplace, QR handover confirmation, digital payment recording, ledger audit view. |
| **AI / ML Pipeline (`ai/`, `Ecobridge-google-collab/`)** | TensorFlow / Keras, TensorFlow Lite, OpenCV, MobileNetV2, synthetic & real e-waste vision datasets | On-device 8-class e-waste vision classifier, export to `mobilenet_scrap_v1.tflite`, calibrated feature fallback. |
| **Cloud & Deployment** | Render (`render.yaml`), Vercel (`vercel.json`), Docker (`backend/Dockerfile`) | Cloud hosting for FastAPI backend (Render) and Recycler Portal (Vercel) with production HTTPS and automated CI/CD. |

---

## 3. Core System Architecture & Directory Map

```text
Ecobridge-repo/
├── backend/                       # ACTIVE FastAPI async backend server
│   ├── src/
│   │   ├── api/v1/endpoints/      # API Routes: auth, lots, sync, pricing, recyclers, recycler_portal, matching
│   │   ├── core/                  # Database config, security, exceptions, and bootstrap.py (auto-seeds catalog)
│   │   ├── models/                # SQLAlchemy ORM models (User, Lot, HandoverRecord, CustodyEvent, etc.)
│   │   ├── schemas/               # Pydantic validation schemas
│   │   └── services/              # Business logic & domain services
│   ├── tests/                     # 18 passing pytest async unit & integration tests
│   ├── Dockerfile                 # Container build for backend
│   └── render.yaml                # Render service definition
│
├── collector_app/                 # ACTIVE Native Android Collector Client
│   ├── app/src/main/
│   │   ├── java/com/ecobridge/
│   │   │   ├── ai/                # ScrapClassifier.java (TFLite interpreter + feature fallback)
│   │   │   ├── audio/             # AudioPromptManager.java (Hindi, Marathi, English voice prompts)
│   │   │   ├── camera/            # CameraManager.java (CameraX photo capture)
│   │   │   ├── data/local/        # Room Database, DAOs, and Entities
│   │   │   ├── data/remote/       # Retrofit REST API client & DTOs
│   │   │   ├── sync/              # SyncWorker.java (WorkManager background sync)
│   │   │   └── ui/                # Activities: Home, NewLot, Handover, PriceBoard, Earnings, Recyclers
│   │   ├── assets/                # labels.txt (8 e-waste classes) & mobilenet_scrap_v1.tflite
│   │   └── res/                   # Vernacular strings (values, values-hi, values-mr), layouts, drawables
│   └── build/outputs/apk/debug/   # Built installable Android APK (~25MB)
│
├── recycler_portal/               # ACTIVE Next.js 14 Recycler Web Portal
│   ├── app/
│   │   ├── dashboard/             # Overview, Handover confirmation, Materials marketplace, Ledger, Payouts
│   │   ├── login/                 # Phone/OTP recycler authentication
│   │   └── lib/api.ts             # API client with token management and proxy routing
│   ├── vercel.json                # Vercel deployment configuration
│   └── next.config.js             # Configured reverse-proxy for /api/v1/* calls
│
├── ai/                            # AI Training & Export Scripts
│   ├── export_ondevice_classifier.py  # Script to train & export TFLite 8-class model
│   └── train_ewaste_classifier.ipynb  # Google Colab notebook for MobileNetV2 fine-tuning
│
├── datasets/                      # Datasets & Catalog Seeds
│   ├── ai_ml/vision/              # E-waste training images, annotations, and split classes
│   └── database_seeds/            # SQL schemas and pricing seed data
│
├── render.yaml                    # Root Render Blueprint for one-click cloud backend hosting
└── CONTEXT.md                     # THIS MASTER CONTEXT DOCUMENT
```

> **Note on legacy directories:**  
> - `apps/api-server/` and `apps/collector-mobile/` (React Native Expo) were early prototypes. **`backend/`** and **`collector_app/`** are the authoritative production codebases.

---

## 4. The 8 Standard E-Waste Classes & Safety Rules

The entire platform (Android, Backend, and Recycler Portal) strictly shares an identical 8-category taxonomy:

| Category Code | Display Name | Benchmark Rate | Safety Severity & Protocol |
|---|---|---|---|
| `CAT_BATTERY` | **Batteries** | ₹105 / kg | **HAZARD**: Swelling/fire risk. Do not puncture, crush, or burn. |
| `CAT_CRT` | **CRT Monitors & TVs** | ₹45 / kg | **HAZARD**: High-voltage vacuum implosion & toxic lead phosphor. Wear heavy gloves. |
| `CAT_PCB` | **Printed Circuit Boards (PCBs)** | ₹330 / kg | **WARNING**: Contains lead/cadmium solder. Avoid bare skin contact. |
| `CAT_LCD_LED` | **LCD / LED Panels** | ₹85 / kg | **WARNING**: Mercury backlight tubes in older CCFL units. |
| `CAT_CABLES` | **Copper Cables & Wires** | ₹195 / kg | **NORMAL**: Stripping safety; fair market weight valuation. |
| `CAT_MOTORS` | **Motors & Magnet Assemblies** | ₹55 / kg | **NORMAL**: Heavy lift hazard; copper winding extraction. |
| `CAT_PLASTICS` | **Mixed E-Waste Plastics** | ₹22 / kg | **NORMAL**: Flame retardant plastics; separate from household scrap. |
| `CAT_OTHER` | **Other Electronic Scrap** | ₹40 / kg | **NORMAL**: Unclassified electronic items. |

---

## 5. End-to-End Lifecycle & Data Flow

```
[Collector Phone]
   │
   ├─ 1. Offline Lot Creation
   │     Take photo (CameraX) ➔ AI Classifier detects category & hazard
   │     Enter weight (kg) ➔ Price benchmark calculated
   │     Persist immediately to SQLite/Room database
   │
   ├─ 2. Delta Background Sync
   │     WorkManager triggers when network is available
   │     POST /api/v1/sync/batch (Idempotent by collector + lot short code)
   │     POST /api/v1/lots/{id}/photos (SHA-256 verified)
   │
[FastAPI Backend]
   │
   ├─ 3. Verification & Staging
   │     Validates payload, creates Lot record, and appends initial CustodyEvent
   │     Available in Recycler Marketplace (GET /api/v1/recycler-portal/materials)
   │
[Recycler Portal (Next.js)]
   │
   ├─ 4. Discovery & In-Person Handover
   │     Recycler inspects lot details, GPS location, and photo
   │     In-person meeting: Collector displays QR code / short code
   │     Recycler scans/enters code: POST /api/v1/recycler-portal/handovers/{ref}/confirm
   │     Recycler enters verified scale weight
   │
[Settlement & Audit Trail]
   │
   ├─ 5. Cryptographic Custody & Payment
   │     Backend locks batch status to VERIFIED/TRANSFERRED
   │     Appends SHA-256 hashed CustodyEvent (Actor ID, timestamp, previous hash)
   │     Payment recorded as PAID; Collector app updates via GET /api/v1/sync/status
```

---

## 6. Verified Working Features & Current Status

### What is 100% Implemented & Tested:
1. **Android App (`collector_app`)**:
   - Compiles cleanly (`assembleDebug` succeeds).
   - Generates standalone APK at [`collector_app/app/build/outputs/apk/debug/app-debug.apk`](file:///c:/Users/admin/Downloads/Ecobridge-repo/collector_app/app/build/outputs/apk/debug/app-debug.apk) and [`C:\Users\admin\Downloads\EcoBridge-Collector-v1.0.apk`](file:///C:/Users/admin/Downloads/EcoBridge-Collector-v1.0.apk).
   - Vernacular audio and multilingual UI (Hindi, Marathi, English).
   - `ScrapClassifier.java` supports dual-mode: TFLite model inference when present, with a calibrated on-device feature-based fallback that reliably detects all 8 categories with hazard alerts.
   - Cleartext HTTP allowed for emulator/local testing, HTTPS default for cloud.
   - Auto-retry sync with `SyncWorker`.

2. **Backend API (`backend`)**:
   - Running live on `http://localhost:8000` (`/docs` OpenAPI available).
   - 18 automated tests passing (`pytest tests/`).
   - Auto-bootstrap on launch seeds the 8-class catalog, price bands, and a test verified recycler company.
   - Idempotent batch sync (`/api/v1/sync/batch`), photo uploads with SHA-256 hash checks, and handover confirmations.
   - Payment endpoints update `HandoverRecord.payment_status` to `PAID` with ledger entries.

3. **Recycler Portal (`recycler_portal`)**:
   - Running live on `http://localhost:3001`.
   - Production build (`npm run build`) succeeds with zero errors (all 10 static/dynamic routes compiled).
   - Built-in Next.js proxy rewrites `/api/v1/*` to the active backend (configurable via `NEXT_PUBLIC_API_URL` or `BACKEND_API_URL`).

4. **Cloud Deployment Readiness**:
   - `render.yaml` configured at root for one-click backend deployment on Render.
   - `recycler_portal/vercel.json` and dynamic Next.js API rewrites configured for Vercel deployment.
   - Git repository clean and synchronized on branch `feature/backend-postgres`.

---

## 7. Guidelines for Any Future AI Working on This Codebase

When continuing development or adding features, follow these strict rules:

1. **Offline Invariant:** Never make the mobile client depend on immediate server connectivity. Everything must be saved to Room DB first, then queued through WorkManager.
2. **Taxonomy Integrity:** Never hardcode new material categories in UI files. Any category must exist in the 8-class catalog (`CAT_BATTERY`, `CAT_CRT`, `CAT_PCB`, `CAT_LCD_LED`, `CAT_CABLES`, `CAT_MOTORS`, `CAT_PLASTICS`, `CAT_OTHER`).
3. **Safety First:** AI predictions must show hazard advisories (PPE requirements, handling warnings) before displaying estimated monetary earnings.
4. **Idempotent Handshakes:** The mobile app's local SQLite ID is not the server's ID. Always correlate using the generated `lot_code` / short reference and collector token.
5. **No Secrets in Repo:** Never commit `.env` files, production JWT secrets, or cloud credentials.

---

## 8. Strategic Expansion Roadmap: Urban Mining, Deep Material AI & Scrapper Flywheel

The project is expanding from a simple collection logging tool into a comprehensive **AI-driven Urban Mining & Workforce Formalization Platform**:

### 1. Android Core Upgrades (Section 5.3 Priorities)
- **TFLite Model Embedding**: `mobilenet_scrap_v1.tflite` embedded in `assets/` with direct-stream memory loading and pure CPU fallback for 100% device compatibility.
- **Move Cleartext to Debug-Only**: `app/src/debug/AndroidManifest.xml` retains `usesCleartextTraffic="true"` for local test servers; release builds enforce TLS 1.3 HTTPS.
- **GPS Location Geotagging**: Capturing fine-accuracy latitude/longitude via `FusedLocationProviderClient` attached to `LotEntity` for regional scrap heatmaps and fraud prevention.
- **Sync Status Badges**: Visual indicator pills (`PENDING`, `SYNCING`, `SYNCED`, `FAILED` with manual retry) in transaction views.

### 2. Deep Material Intelligence & Urban Mining AI
- **Elemental Bill of Materials (BOM)**: Decomposing collected scrap into recoverable precious and rare metals:
  - Gold (Au), Silver (Ag), Copper (Cu), Palladium (Pd), Cobalt (Co), Lithium (Li), Neodymium (Nd).
- **Hazard Matrix**: Safety warnings (PPE, thermal runaway, HF acid, lead oxide, mercury vapor) prioritized before financial estimates.
- **Robustness in Unclear / Messy Scrap**: Upgrading from single-label MobileNet to YOLOv8-Nano object detection with CLAHE lighting normalization for dirty, tangled scrap heaps.

### 3. Recycler Smelting Economics & EPR Ledger
- **Recovery Yield % Engine**: Computes exact net realization based on metal spot prices (MCX/LME) and hydrometallurgical smelting efficiencies.
- **CPCB EPR Certificate Automation**: Translates verified processed volumes into official CPCB compliance certificates for corporate electronic brands.

### 4. Collector Gamification & Incentive Flywheel
- **Daily Quotas & Streak Bonuses**: Instant cash / UPI rewards for daily volume milestones (e.g. 15 kg/day $\rightarrow$ +₹50 bonus).
- **Green Dividend Pass-Through**: Routing ₹3–5/kg of corporate EPR compliance revenue directly to the informal waste picker.
- **Aggregator Hub (*Kabadi Dukaan*) Franchising**: Providing neighborhood scrap shop owners with a 1.5% aggregation fee to turn them into certified collection hubs.

---

## 9. DPDP Act (2023) Compliance, Privacy Architecture & Final Submission Strategy

### 1. Indian DPDP Act 2023 Compliance Framework
- **Notice & Consent (Sections 5 & 6)**: Multi-lingual affirmative consent notice (Marathi, Hindi, English) with voice playback for low-literacy informal waste pickers.
- **Data Minimization (Section 7)**: ZERO collection of Aadhaar numbers, biometric facial scans, phone contact books, or SMS logs.
- **Child Labor Safeguards (Section 9)**: Mandatory age verification ($\ge 18$) to prevent informal child labor in scrap handling.
- **Right to Erasure (Section 12)**: Collector can purge personal profile data; statutory scrap audit hashes remain anonymized for CPCB compliance.
- **Data Protection Officer (Section 13)**: Formal DPO escalation contact with statutory 7-day grievance SLA.

### 2. Android Runtime Permissions & Scoped Storage
- **Just-in-Time Rationale**: Rationale cards explain *why* camera or GPS is required before triggering system dialogs.
- **Permissions**: `CAMERA` (lot photos/scale OCR), `ACCESS_FINE_LOCATION` (scrap origin geotagging only while app in use), `POST_NOTIFICATIONS` (sync & payout alerts).
- **Excluded**: No background location, no storage permissions (uses Android 10+ scoped storage).

### 3. Competition-Winning Submission Differentiators
- **CPCB / SPCB Regulatory Portal**: Real-time municipal e-waste heatmaps and automated EPR compliance manifests.
- **Carbon Offset & ESG Metric Engine**: Calculates exact kg $CO_2$ and liters of water saved per lot recycled.
- **Merkle Tree Cryptographic Batch Verification**: Immutable lot aggregation proof for truckload delivery.
- **Hazard & PPE Verification**: AI verifies protective gear (gloves, eyewear) before handling swollen batteries or broken CRT glass.
- **Offline Cryptographic Cash Vouchers**: Signed offline QR vouchers for zero-connectivity scrap yard handovers.


