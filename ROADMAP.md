# ECOBRIDGE — Strategic Master Roadmap & Milestone Tracker

> **Project Name:** ECOBRIDGE (SIH 2026 PS 26229 — *Kabadiwala Connect*)  
> **Repository:** `atharvashivdikar01-stack/Ecobridge`  
> **Status:** Active Development & Feature Expansion  
> **Last Updated:** September 2026  

---

## 1. Overall Progress Matrix

```
┌───────────────────────────────────────────────────────────────┐
│  Phase 1: Foundations & Demo Completeness        [ 100% DONE ] │
│  Phase 2: Data Trust, AI & Deep Material BOM    [ 70% ACTIVE ]│
│  Phase 3: Production Scale & Cloud Hardening     [ 40% ACTIVE ]│
│  Phase 4: CPCB EPR Compliance & SIH Finale       [ 30% QUEUED ]│
└───────────────────────────────────────────────────────────────┘
```

---

## 2. Phase 1: Foundations & Demo Completeness (Status: 100% COMPLETED)

Goal: Achieve seamless end-to-end data flow from collector Android client to FastAPI backend to Next.js Recycler Portal.

- [x] **Core Taxonomy Alignment:** Unified 8-class e-waste catalog across Android, backend, and portal (`CAT_BATTERY`, `CAT_CRT`, `CAT_PCB`, `CAT_LCD_LED`, `CAT_CABLES`, `CAT_MOTORS`, `CAT_PLASTICS`, `CAT_OTHER`).
- [x] **Auto-Bootstrap Database:** Database seeds benchmark prices, categories, and verified local test recycler on startup.
- [x] **FastAPI Async Backend:** 18 automated pytest tests passing cleanly, including round-trip sync, photo hashing, and handover confirmation.
- [x] **Offline-First Android Client:** Native Java Android app with Jetpack Room (SQLite) offline storage, WorkManager background sync queue, and CameraX photo capture.
- [x] **On-Device AI Classification:** Embedded `mobilenet_scrap_v1.tflite` model with dual-mode fallback feature analyzer and `labels.txt`.
- [x] **Next.js Recycler Web Portal:** Production build succeeds with 10 static/dynamic pages for lot browsing, weighbridge handover, payments, and ledger view.
- [x] **Tamper-Evident SHA-256 Ledger:** Custody transitions logged with actor ID, timestamp, and previous hash verification.
- [x] **Local Demo Verification:** Verified complete journey: Offline lot creation -> WorkManager batch sync -> Recycler acceptance -> Weighbridge handover -> Payment settlement -> Status update.

---

## 3. Phase 2: Data Trust, AI & Deep Material Intelligence (Status: IN PROGRESS)

Goal: Expand from simple collection logging into an AI-powered Urban Mining & Material Intelligence platform.

### A. Pricing & Market Intelligence
- [x] **Dynamic Price Intelligence Router:** Backend `/api/v1/prices/intelligence/{id}` for empirical observations and statistical estimates.
- [ ] **Unified Benchmark Endpoint (`GET /api/v1/prices`):** Return all 8 active categories with current benchmark price/kg, price bands, and safety warnings for mobile caching.
- [ ] **Real-time Recycler Quotations:** Allow recyclers to broadcast custom premium pricing for specific high-value categories (e.g., high-grade telecom PCBs).

### B. Mobile Client Enhancements (`collector_app`)
- [x] **Vernacular Audio Prompts:** English, Hindi, and Marathi voice prompt architecture via `AudioPromptManager`.
- [ ] **Dynamic Server URL Configuration:** Allow specifying local LAN IP or Render cloud URL without recompiling APK.
- [ ] **Fine-Accuracy Geotagging:** Capture GPS coordinates on lot creation (`FusedLocationProviderClient`) for scrap density heatmaps and anti-fraud validation.
- [ ] **Visual Sync Pills:** Add status badges (`SYNCED`, `PENDING_SYNC`, `SYNCING`, `ERROR`) in lot lists and transaction views.
- [ ] **Hazard Safety Pre-Screen:** Force full-screen PPE alert card before price display when CRT or battery hazards are detected.

### C. Recycler Portal Upgrades (`recycler_portal`)
- [ ] **Urban Mining Elemental BOM Calculator:** Decompose scrap weight into projected recoverable gold (Au), silver (Ag), copper (Cu), cobalt (Co), and lithium (Li) yields.
- [ ] **CPCB EPR Compliance Manifest Exporter:** One-click download of statutory Form-6 / EPR transfer manifests in PDF/CSV format.
- [ ] **Real-time Metrics Dashboard:** Active charts for daily intake weight, total settlement value, and carbon offset calculations ($kg\ CO_2$ averted).

---

## 4. Phase 3: Production Scale, DPDP Compliance & Cloud (Status: IN PROGRESS)

Goal: Harden security, comply with Indian DPDP Act 2023, and deploy scalable cloud infrastructure.

### A. Cloud Hosting & CI/CD
- [x] **Render Backend Configuration:** `render.yaml` blueprint configured at repository root.
- [x] **Vercel Web Portal Configuration:** `recycler_portal/vercel.json` configured with reverse-proxy rewrites.
- [ ] **PostgreSQL Migration Automation:** Automated Alembic migration pipeline against managed PostgreSQL (Supabase / Neon / Render Postgres).
- [ ] **Cloud Storage for Scrap Photos:** Cloudflare R2 / AWS S3 integration for verified scrap imagery with signed pre-authenticated URLs.

### B. Indian DPDP Act (2023) Privacy Architecture
- [ ] **Affirmative Multi-Lingual Consent Screen:** Hindi, Marathi, and English consent dialogue with audio readout for illiterate scrap collectors.
- [ ] **Zero High-Risk Data Collection:** Explicit prohibition and exclusion of Aadhaar numbers, biometric scans, and address books.
- [ ] **Child Labor Safeguard Check:** Explicit age gate ($\ge 18$) to enforce non-involvement of minors in hazardous scrap sorting.
- [ ] **Right to Erasure & DPO Contact:** Profile deletion interface preserving only anonymized cryptographic custody hashes for statutory audits.

### C. Scalable Authentication
- [ ] **Production SMS Gateway:** Fast2SMS / MSG91 integration with Android SMS Retriever API for 1-tap OTP verification.
- [ ] **Truecaller SDK Integration:** Instant mobile number verification for waste pickers with zero manual typing.
- [ ] **Role-Based Access Control (RBAC):** Strict JWT separation between `COLLECTOR`, `RECYCLER_OPERATOR`, `RECYCLER_ADMIN`, and `REGULATOR`.

---

## 5. Phase 4: CPCB ESG Compliance, Traceability & Finale (Status: QUEUED)

Goal: Differentiate EcoBridge for SIH 2026 grand finale presentation with tangible institutional impact.

- [ ] **Merkle Tree Batch Verification:** Cryptographic batching of multiple collector lots into single verified truckload manifests.
- [ ] **Green Dividend Mechanism:** Automated ledger pass-through routing ₹3–5/kg of corporate EPR compliance credits directly to the original waste collector's wallet.
- [ ] **Aggregator Hub (*Kabadi Dukaan*) Franchising:** Multi-tier support for neighborhood scrap shops operating as certified aggregation micro-hubs.
- [ ] **Municipal E-Waste Heatmap:** Real-time spatial map for municipal corporations and state pollution control boards (SPCBs) showing collection volume density.
- [ ] **Offline Cryptographic Cash Vouchers:** Signed offline QR payment vouchers for remote scrap yards with zero cell connectivity.

---

## 6. Living Task Tracking Table

| ID | Task Description | Target Component | Priority | Status |
|---|---|---|---|---|
| T-101 | Implement `GET /api/v1/prices` benchmark endpoint | `backend` | High | ✅ COMPLETED |
| T-102 | Clean URL configuration & dynamic server endpoint | `collector_app` | High | ✅ COMPLETED |
| T-103 | Build Urban Mining Recovery Calculator | `recycler_portal` | High | ✅ COMPLETED |
| T-104 | Generate CPCB Form-6 EPR Manifest exporter | `recycler_portal` | Medium | ✅ COMPLETED |
| T-105 | Add GPS Geotagging to `LotEntity` | `collector_app` | Medium | 📋 PLANNED |
| T-106 | Full-screen PPE hazard dialog on critical scrap | `collector_app` | Medium | ✅ COMPLETED |
| T-107 | Cloud deployment configuration for Render & Vercel live URLs | `infra` | High | ✅ READY TO HOST |
| T-108 | DPDP Act 2023 Consent & Age Gate screen | `collector_app` | Medium | 📋 PLANNED |
| T-109 | Build CPCB & Regulator Admin Dashboard Portal | `admin_dashboard` | High | ✅ COMPLETED |
| T-110 | Enforce unavoidable atomic custody events on all lot transitions | `backend` | High | ✅ COMPLETED |
| T-111 | Correct mobile handover wording and non-misleading status | `collector_app` | High | ✅ COMPLETED |
| T-112 | Gate demo OTP 123456 behind DEMO_MODE & validate production secrets | `backend` | High | ✅ COMPLETED |
| T-113 | Add illustrative demo banners & fix price mapping in admin dashboard | `admin_dashboard` | High | ✅ COMPLETED |
| T-114 | Block synthetic demo fallback images from custody evidence sync | `collector_app` | High | ✅ COMPLETED |
| T-116 | Configure authoritative Alembic migrations & initial schema revision | `backend` | High | ✅ COMPLETED |
