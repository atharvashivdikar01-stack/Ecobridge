# SMART INDIA HACKATHON 2026
## OFFICIAL PORTAL SUBMISSION & EVALUATION DOSSIER

**Problem Statement ID:** 26229  
**Problem Statement Title:** Formalizing the Informal E-Waste Economy (Kabadiwala Connect)  
**Project Name:** ECOBRIDGE (कबाड़ीवाला कनेक्ट)  
**Theme:** Clean & Green Technology / Urban Mining & Circular Economy  
**Category:** Software + Edge AI  

---

### 1. Key Submission Links & Media Assets

- **YouTube Video Demo Link:** `[PASTE YOUR YOUTUBE VIDEO LINK HERE]`
- **Presentation Deck (PPT):** `[ATTACH YOUR PRESENTATION PPT HERE]`
- **GitHub Repository:** [https://github.com/atharvashivdikar01-stack/Ecobridge](https://github.com/atharvashivdikar01-stack/Ecobridge)
- **Direct APK Download (v1.2.0):** [Download EcoBridge-Collector-v1.2.apk](https://github.com/atharvashivdikar01-stack/Ecobridge/raw/main/release/EcoBridge-Collector-v1.2.apk)
- **GitHub Release Tag (v1.2.0):** [https://github.com/atharvashivdikar01-stack/Ecobridge/releases/tag/v1.2.0](https://github.com/atharvashivdikar01-stack/Ecobridge/releases/tag/v1.2.0)

---

### 2. Live Production Deployments & Evaluator Credentials

All platforms, cloud microservices, and mobile binaries are 100% live and fully deployed:

| Platform Component | Production URL | Access & Credentials |
|---|---|---|
| **Certified Recycler Operations Portal** | [https://ecobridge-recycler-portal.vercel.app](https://ecobridge-recycler-portal.vercel.app) | **1-Click Demo Login** OR<br>Phone: `+919811111111`<br>OTP: `123456` |
| **CPCB Regulator & Platform Admin** | [https://ecobridge-admin-dashboard.vercel.app](https://ecobridge-admin-dashboard.vercel.app) | **1-Click Instant Role Switcher**<br>*(Regulator / Platform Admin)* |
| **Live Azure Cloud API & Swagger** | [https://ecobridge-api-sih26-d3hfbccrg3fpddcr.centralindia-01.azurewebsites.net/docs](https://ecobridge-api-sih26-d3hfbccrg3fpddcr.centralindia-01.azurewebsites.net/docs) | Interactive Swagger UI (35+ Endpoints) |
| **Backend Health Check Status** | [https://ecobridge-api-sih26-d3hfbccrg3fpddcr.centralindia-01.azurewebsites.net/api/v1/health](https://ecobridge-api-sih26-d3hfbccrg3fpddcr.centralindia-01.azurewebsites.net/api/v1/health) | Live Status: `{"status": "ok", "database": "connected"}` |
| **Collector Android App (v1.2.0)** | [https://github.com/atharvashivdikar01-stack/Ecobridge/raw/main/release/EcoBridge-Collector-v1.2.apk](https://github.com/atharvashivdikar01-stack/Ecobridge/raw/main/release/EcoBridge-Collector-v1.2.apk) | **1-Click Online Login (Raju Shinde)**<br>OR **100% Offline Mode** |

---

### 3. Executive Summary

Over **90% of India's electronic waste** is handled by the unorganized informal sector—over 1.5 million waste pickers and local scrap aggregators (*kabadiwalas*). Informal workers recover crucial secondary raw materials (copper, gold, rare-earths), yet endure predatory middleman price deductions, hazardous open-acid leaching and battery fire risks, complete exclusion from formal credit and banking, and zero GST inclusion. Meanwhile, certified formal recyclers struggle to obtain genuine scrap to fulfill statutory Extended Producer Responsibility (EPR) targets due to opaque supply chains.

**ECOBRIDGE** formalizes India's informal e-waste economy through a unified three-tier digital architecture:
1. An **offline-first Android Mobile App** powered by an on-device Edge AI Vision classifier (<150ms inference), safety-first PPE hazard protocols, and vernacular audio guidance in Marathi, Hindi, and English.
2. A **FastAPI async backend on Azure Cloud** computing real-time CPCB market benchmark pricing, automated 5% Reverse GST under HSN 8548/8549, and digital weight reconciliation.
3. A **Certified Recycler Operations Portal** and **CPCB Regulator Dashboard** enforcing an unbroken, tamper-evident SHA-256 cryptographic chain of custody and generating statutory CPCB Form-6 Manifests.

---

### 4. Key Technical Innovations

1. **On-Device Edge AI Vision Classifier (TFLite 2.16.1):**
   - Custom-quantized MobileNetV2 (`mobilenet_scrap_v1.tflite`, 2.5 MB) running completely on-device in **sub-150ms** without cellular connectivity.
   - Core Safety Invariant: Before rendering any financial valuation, ECOBRIDGE automatically displays mandatory PPE and safety warnings (swollen lithium-ion battery fire hazard, leaded CRT implosion danger, burnt PCB toxic fumes).
2. **Tamper-Evident SHA-256 Chain of Custody:**
   - Every physical handover computes an immutable cryptographic digest:
     $$\text{Hash} = \text{SHA-256}(\text{LotUUID} \parallel \text{RecyclerID} \parallel \text{NetWeight} \parallel \text{TaxInvoice} \parallel \text{PrevHash} \parallel \text{Timestamp})$$
   - Generates statutory **Form-6 CPCB E-Waste Manifests** with cryptographic verification.
3. **Vernacular Voice-First UX (Marathi / Hindi / English):**
   - 100% tri-lingual parity with high-fidelity human studio audio prompts (`.ogg`) and automated `0.95x` TTS fallback designed specifically for noisy scrap yard environments and illiterate workers.
4. **Automated 5% Reverse GST & Physical Cash Counter:**
   - Automatic 5% GST computation (2.5% CGST + 2.5% SGST) under HSN 8548/8549 with statutory invoice numbering (`TXI-YYYY-STATE-XXXXXX`).
   - Integrated physical currency denomination counter with greedy change algorithm for zero-discrepancy gate settlements.
5. **Digital Personal Data Protection (DPDP) Act 2023 Compliance:**
   - Zero storage of Aadhaar numbers or biometrics.
   - Plain-language vernacular audio consent notices and mandatory age gate ($\ge 18$) to prevent child labor in informal recycling.

---

### 5. 5-Minute Evaluator Verification Checklist

- [x] **Step 1: Install & Test Android App:** Download `EcoBridge-Collector-v1.2.apk`. Tap `⚡ 1-Click Online Login (Raju Shinde)`.
- [x] **Step 2: Create a Scrap Lot:** Select material (e.g. *Batteries*), inspect on-device AI PPE hazard warning, enter weight (15 kg), inspect 5% GST and benchmark pricing. Tap Save Lot to generate tamper-evident QR code.
- [x] **Step 3: Web Marketplace Inwarding:** Open Recycler Portal, click 1-Click Demo Recycler Login. Open Materials Marketplace, view incoming lot, record weighbridge tare/gross readings, and settle payment via Cash or UPI.
- [x] **Step 4: Statutory Form-6 Generation:** In Recycler Portal, open Ledger and download the generated CPCB Form-6 E-Waste Manifest with SHA-256 digital signatures.
- [x] **Step 5: CPCB Regulator Heatmaps:** Open Admin Dashboard to view city-wide flow heatmaps, EPR compliance charts, and DPDP audit logs.
