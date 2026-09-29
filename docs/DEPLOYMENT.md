# ECOBRIDGE — Complete Cloud Deployment Guide
## Smart India Hackathon 2026 | Problem Statement 26229

> **Last verified:** 29 September 2026  
> **All subsystems tested:** 21/21 backend tests ✅ | 12+10 Next.js routes built ✅ | Android APK 29.4 MB ✅

---

## ⚡ Quick Reference: What Gets Deployed Where

| Component | Platform | Cost | Card Required? |
|---|---|---|---|
| **FastAPI Backend** | **Koyeb** | 🆓 Free | ❌ No |
| **Recycler Portal** | **Vercel** | 🆓 Free | ❌ No |
| **Admin Dashboard** | **Vercel** | 🆓 Free | ❌ No |
| **Android APK** | **GitHub** | 🆓 Free | ❌ No |

> ⚠️ **Note on Render:** Render now requires a credit card even for its free tier. We use **Koyeb** instead — 100% free, no card ever required.

---

## PHASE 1 — Push Latest Code to GitHub

> ✅ Already done! The repo at `atharvashivdikar01-stack/Ecobridge` (branch `main`) is up-to-date and clean.

If you ever need to re-push:
```powershell
cd C:\Users\admin\Downloads\Ecobridge-repo
git add -A
git commit -m "chore: deployment ready"
git push origin main
```

---

## PHASE 2 — Deploy Backend to Koyeb (FREE, No Card)

### 2.1 Create Your Koyeb Account

1. Open **[https://app.koyeb.com/](https://app.koyeb.com/)** in your browser.
2. Click **Sign up** → Choose **"Continue with GitHub"**.
3. Authorize Koyeb to access your GitHub account.
4. You are now inside the Koyeb dashboard. **No credit card is asked.**

---

### 2.2 Deploy the Backend Service

1. Click **"Create App"** (big button in the middle of the dashboard).
2. Select **"GitHub"** as your deployment source.
3. In the repository search, choose **`atharvashivdikar01-stack/Ecobridge`**.
4. Set **Branch** to: `main`
5. Set **Build & deployment settings:**

   | Setting | Value |
   |---|---|
   | **Service type** | Web service |
   | **Builder** | Buildpack (automatic) |
   | **Root directory** | `backend` |
   | **Run command** | `alembic upgrade head && uvicorn src.main:app --host 0.0.0.0 --port 8000` |
   | **Port** | `8000` |
   | **Instance type** | Free |

6. Scroll down to **Environment variables**. Click **+ Add variable** for each:

   | Key | Value |
   |---|---|
   | `DATABASE_URL` | `sqlite+aiosqlite:///./data/ecobridge.db` |
   | `DEMO_MODE` | `true` |
   | `SECRET_KEY` | `ecobridge2026sih26229hackathon!!` |
   | `CORS_ORIGINS` | `*` |
   | `ACCESS_TOKEN_EXPIRE_MINUTES` | `10080` |
   | `PYTHONPATH` | `backend` |

7. Click **"Deploy"** at the bottom.

---

### 2.3 Wait for Build & Verify

- Build takes approximately **3–5 minutes** the first time.
- Once you see **"Healthy"** status (green dot), your backend is live.
- Your URL will look like: `https://ecobridge-xxxx.koyeb.app`

**✅ Verify by opening in browser:**
```
https://ecobridge-xxxx.koyeb.app/docs
```
You should see the interactive FastAPI Swagger documentation with all your endpoints listed.

**✅ Test a quick API call:**
```
https://ecobridge-xxxx.koyeb.app/api/v1/materials/taxonomy
```
Should return a JSON list of 8 material categories.

> 📌 **COPY THIS URL — you will need it for Vercel.**

---

## PHASE 3 — Deploy Recycler Portal to Vercel (FREE, No Card)

### 3.1 Create Vercel Account

1. Open **[https://vercel.com/](https://vercel.com/)**.
2. Click **"Sign Up"** → Choose **"Continue with GitHub"**.
3. Authorize Vercel. **No credit card required at any point.**

---

### 3.2 Import Recycler Portal

1. Once inside the Vercel dashboard, click **"Add New..."** → **"Project"**.
2. In the "Import Git Repository" list, find `atharvashivdikar01-stack/Ecobridge` and click **"Import"**.
3. Vercel will show the project configuration screen. Set:

   | Setting | Value |
   |---|---|
   | **Project Name** | `ecobridge-recycler-portal` |
   | **Framework Preset** | Next.js (auto-detected) |
   | **Root Directory** | Click **"Edit"** → type `recycler_portal` → click **"Continue"** |
   | **Build Command** | (leave default: `npm run build`) |
   | **Output Directory** | (leave default: `.next`) |
   | **Install Command** | (leave default: `npm install`) |

4. Scroll down to **"Environment Variables"**. Add:

   | Name | Value |
   |---|---|
   | `NEXT_PUBLIC_API_URL` | `https://ecobridge-xxxx.koyeb.app` *(your Koyeb URL from Phase 2)* |

5. Click **"Deploy"**.
6. Build completes in ~60 seconds.
7. Your URL will be: `https://ecobridge-recycler-portal.vercel.app`

**✅ Verify:** Open the URL → should show the EcoBridge login page. Click **"Demo Login"** → should log in with `+919811111111` and OTP `123456`.

---

## PHASE 4 — Deploy Admin Dashboard to Vercel (FREE, No Card)

1. In Vercel dashboard, click **"Add New..."** → **"Project"** again.
2. Import the **same repository** `atharvashivdikar01-stack/Ecobridge`.
3. Configure:

   | Setting | Value |
   |---|---|
   | **Project Name** | `ecobridge-admin-dashboard` |
   | **Framework Preset** | Next.js |
   | **Root Directory** | Click **"Edit"** → type `admin_dashboard` → click **"Continue"** |

4. Environment Variables:

   | Name | Value |
   |---|---|
   | `NEXT_PUBLIC_API_URL` | `https://ecobridge-xxxx.koyeb.app` *(same Koyeb URL)* |

5. Click **"Deploy"**.
6. Your URL will be: `https://ecobridge-admin-dashboard.vercel.app`

**✅ Verify:** Open the URL → should see the CPCB Regulator dashboard with the amber "⚠️ Illustrative Demonstration Panel" banner and real benchmark pricing data loaded.

---

## PHASE 5 — Android APK Distribution

The pre-built APK is already committed to GitHub and available for **direct download** without any sign-in:

```
https://github.com/atharvashivdikar01-stack/Ecobridge/raw/main/release/EcoBridge-Collector-v1.0.apk
```

**To install on an Android phone:**
1. Open the above URL on an Android phone.
2. Tap **Download** → once downloaded, tap the `.apk` file.
3. If prompted "Install from unknown sources" → tap **Settings** → enable → go back and install.
4. Open **EcoBridge** app.

---

## PHASE 6 — Update README with Live URLs

Once all three platforms are live, update the README's evaluation table. Run:

```powershell
cd C:\Users\admin\Downloads\Ecobridge-repo
# Edit README.md with your live URLs, then:
git add README.md
git commit -m "docs: add live deployment URLs for judge evaluation"
git push origin main
```

---

## Final Checklist Before Sharing with Judges

- [ ] `https://ecobridge-xxxx.koyeb.app/docs` — Swagger UI loads ✅
- [ ] `https://ecobridge-xxxx.koyeb.app/api/v1/materials/taxonomy` — Returns 8 categories ✅
- [ ] Recycler Portal login with `+919811111111` / `123456` works ✅
- [ ] Admin Dashboard loads with demo banner ✅
- [ ] APK installs and launches on Android 8.0+ ✅

---

## Demo Credentials (Share with Judges)

```
====================================================================
ECOBRIDGE — SIH 2026 Problem Statement 26229 (Kabadiwala Connect)
====================================================================

🌐 Recycler Portal:     https://ecobridge-recycler-portal.vercel.app
📊 CPCB Admin Panel:    https://ecobridge-admin-dashboard.vercel.app
⚡ Backend Swagger API: https://ecobridge-xxxx.koyeb.app/docs
📱 Android APK (v1.0):  https://github.com/atharvashivdikar01-stack/Ecobridge/raw/main/release/EcoBridge-Collector-v1.0.apk

DEMO CREDENTIALS:
  Phone Number: +919811111111
  OTP Code:     123456
====================================================================
```

---

## Troubleshooting

| Problem | Fix |
|---|---|
| Koyeb build fails with "module not found" | Check Root Directory is set to `backend` |
| `alembic upgrade head` fails on Koyeb | The `data/` folder is auto-created by the Dockerfile — if missing, add `RUN mkdir -p data` to Dockerfile |
| Vercel shows blank page | Check `NEXT_PUBLIC_API_URL` env var is set correctly (must not have trailing `/`) |
| OTP `123456` rejected | Verify `DEMO_MODE=true` is set in Koyeb environment variables |
| APK won't install | Enable "Install from Unknown Sources" in Android Settings → Security |
| Admin dashboard shows no pricing data | Backend cold-start — wait 30s and refresh |
