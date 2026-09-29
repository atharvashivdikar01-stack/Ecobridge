# ECOBRIDGE — Cloud Deployment & Judge Evaluation Guide

> **Live Deployment Target:** Today (Free & Simple Hosting for Judges)  
> **Backend Host:** Render (Free Python/Uvicorn Service with SQLite + Alembic)  
> **Web Portals Host:** Vercel (Edge Next.js 14 Hosting for Recycler & Admin Dashboards)  
> **Mobile App:** Native Android APK (`EcoBridge-Collector-v1.0.apk`)

---

## 1. Quick Verification Summary

Before deploying, all subsystems were independently tested and verified:
- **FastAPI Backend:** ✅ 21 / 21 pytest automated tests passing cleanly in 2.6s.
- **Live HTTP Server:** ✅ Tested live boot with Uvicorn; served 8 material categories with pricing bands.
- **Alembic Database:** ✅ Initial schema revision `b9c2401a0dfe` applied and stamped.
- **Recycler Web Portal:** ✅ Production build passes (12 static/dynamic routes compiled).
- **Admin & Regulator Dashboard:** ✅ Production build passes (10 static routes compiled).
- **Android APK:** ✅ Compiled cleanly via Gradle; installable binary generated at `C:\Users\admin\Downloads\EcoBridge-Collector-v1.0.apk` (29.4 MB).
- **Git Repository:** ✅ `git diff --check` passes with zero whitespace or line-ending errors.

---

## 2. Step 1: Commit and Push to GitHub

From the root of `Ecobridge-repo`:

```powershell
git add -A
git commit -m "feat: complete pre-deployment hardening, custody events, and alembic migrations"
git push origin feature/backend-postgres
```

---

## 3. Step 2: Deploy Backend to Render (Free)

1. Open [dashboard.render.com](https://dashboard.render.com).
2. Click **New +** → **Blueprint**.
3. Select your repository: `atharvashivdikar01-stack/Ecobridge`.
4. Choose the branch: `feature/backend-postgres`.
5. Render will automatically read [`render.yaml`](file:///c:/Users/admin/Downloads/Ecobridge-repo/render.yaml) at the repository root.
6. Verify the configured environment variables:
   - `DATABASE_URL`: `sqlite+aiosqlite:///./data/ecobridge.db`
   - `SECRET_KEY`: (Click *Generate* for a random 32+ character key)
   - `ACCESS_TOKEN_EXPIRE_MINUTES`: `10080`
   - `CORS_ORIGINS`: `*`
   - `DEMO_MODE`: `true`
7. Click **Apply**. Render will install requirements, run `alembic upgrade head`, and boot Uvicorn.
8. Copy your live backend URL (e.g., `https://ecobridge-backend.onrender.com`).
9. Verify by opening `https://ecobridge-backend.onrender.com/docs` in your browser.

> ℹ️ *Note for Judges:* Free-tier Render web services spin down after 15 minutes of inactivity. The very first request after idle may take ~30 seconds to cold-start.

---

## 4. Step 3: Deploy Recycler Portal to Vercel (Free)

1. Open [vercel.com](https://vercel.com) and log in.
2. Click **Add New...** → **Project**.
3. Import your GitHub repository (`atharvashivdikar01-stack/Ecobridge`).
4. In the configuration screen:
   - **Project Name:** `ecobridge-recycler-portal`
   - **Framework Preset:** Next.js
   - **Root Directory:** Click *Edit* and select `recycler_portal`
5. In **Environment Variables**, add:
   - `BACKEND_API_URL` = `https://ecobridge-backend.onrender.com` (your Render URL from Step 2)
   - `NEXT_PUBLIC_API_URL` = `https://ecobridge-backend.onrender.com`
6. Click **Deploy**.
7. Vercel will compile the Next.js app in ~60 seconds and assign a URL (e.g., `https://ecobridge-recycler-portal.vercel.app`).

---

## 5. Step 4: Deploy Admin & Regulator Dashboard to Vercel (Free)

1. In Vercel, click **Add New...** → **Project** again.
2. Select the same repository (`atharvashivdikar01-stack/Ecobridge`).
3. In the configuration screen:
   - **Project Name:** `ecobridge-admin-dashboard`
   - **Framework Preset:** Next.js
   - **Root Directory:** Click *Edit* and select `admin_dashboard`
4. In **Environment Variables**, add:
   - `BACKEND_API_URL` = `https://ecobridge-backend.onrender.com`
   - `NEXT_PUBLIC_API_URL` = `https://ecobridge-backend.onrender.com`
5. Click **Deploy**.
6. Vercel will build and assign a URL (e.g., `https://ecobridge-admin-dashboard.vercel.app`).

---

## 6. Step 5: Android APK Installation

The installable Android APK is pre-built on your machine at:
- **Primary:** `C:\Users\admin\Downloads\EcoBridge-Collector-v1.0.apk`
- **Gradle Output:** `C:\Users\admin\Downloads\Ecobridge-repo\collector_app\app\build\outputs\apk\debug\app-debug.apk`

Upload this `.apk` to Google Drive or Firebase App Distribution, set permissions to *"Anyone with the link can view"*, and share the download link with evaluators.

---

## 7. Judge Evaluation & Demo Walkthrough Script

Share the following summary block directly with judges:

```text
======================================================================
ECOBRIDGE — KABADIWALA CONNECT (SIH 2026 PS 26229)
Formalizing the Informal E-Waste Supply Chain with AI & Traceability
======================================================================

🌐 Recycler Operations Portal:  https://ecobridge-recycler-portal.vercel.app
📊 CPCB & Regulator Dashboard:  https://ecobridge-admin-dashboard.vercel.app
⚡ Interactive Backend OpenAPI: https://ecobridge-backend.onrender.com/docs
📱 Collector Mobile APK (v1.0): [PASTE YOUR GOOGLE DRIVE LINK HERE]

DEMO EVALUATION CREDENTIALS:
- Recycler / Collector Phone: +919811111111
- Demo OTP Code:              123456
- Fast-Switch:                1-Click Role Switcher on bottom left

5-MINUTE EVALUATION WALKTHROUGH:
1. Mobile App (Offline Lot Creation):
   - Open app -> Tap "Weigh New Scrap".
   - Take scrap photo -> AI categorizes scrap and triggers mandatory PPE / Hazard warnings.
   - Enter scale weight (kg) -> Transparent market benchmark price is calculated.
   - Save offline -> Staged locally in SQLite Room DB without internet.

2. WorkManager Delta Sync:
   - When connected, background queue syncs lot and photo SHA-256 integrity hash to backend.

3. Recycler Portal:
   - Open Recycler Portal -> Log in with +919811111111 / 123456.
   - Materials Marketplace -> Inspect pending scrap batches.
   - Accept batch -> Confirm weighbridge gross/tare scale weight.
   - Mark as Paid -> Disburses payment.

4. Tamper-Evident Ledger:
   - View Accounting Ledger -> Inspect unbroken SHA-256 chain of custody with actor signatures.
   - CPCB Manifest -> Export statutory Form-6 manifest with SHA-256 verification.

5. CPCB Regulator Panel:
   - Open Admin Dashboard -> Inspect municipal heatmaps, DPDP audit screens, and Green Dividends.
======================================================================
```
