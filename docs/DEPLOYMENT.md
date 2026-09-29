# ECOBRIDGE — Complete Deployment Guide
## Smart India Hackathon 2026 | Problem Statement 26229
### Platform: Azure App Service (Backend) + Vercel (Portals)

> **Status:** Production-Ready | All tests passing ✅

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│              GitHub (atharvashivdikar01-stack)        │
│                  Branch: main                        │
└──────────┬──────────────────────────┬───────────────┘
           │ push triggers             │ push triggers
           ▼                           ▼
┌──────────────────────┐   ┌──────────────────────────┐
│  Azure App Service   │   │         Vercel            │
│  (F1 Free, Always-On)│   │  (Free, Always-On)        │
│                      │   │                           │
│  FastAPI Backend     │   │  recycler_portal  (Next)  │
│  Python 3.11         │   │  admin_dashboard  (Next)  │
│  SQLite + Alembic    │   │                           │
│                      │   │  NEXT_PUBLIC_API_URL ────►│──► Azure URL
└──────────────────────┘   └──────────────────────────┘
           ▲
           │
┌──────────────────────┐
│     GitHub Releases  │
│   Android APK v1.0   │
└──────────────────────┘
```

| Component | Platform | Cost | Always-On | Card? |
|---|---|---|---|---|
| FastAPI Backend | Azure App Service F1 | **$0** | ✅ Yes | ❌ No |
| Recycler Portal | Vercel | **$0** | ✅ Yes | ❌ No |
| Admin Dashboard | Vercel | **$0** | ✅ Yes | ❌ No |
| Android APK | GitHub Releases | **$0** | ✅ Yes | ❌ No |

---

## PRE-REQUISITES

- A **college/university email** address (e.g. `@spit.ac.in`, `@iit*.ac.in`, `@vjti.ac.in`)
- GitHub account: `atharvashivdikar01-stack`

---

## PHASE 1 — Azure for Students Account (5 minutes)

### 1.1 Sign Up (No Credit Card Required)

1. Open **[azure.microsoft.com/free/students](https://azure.microsoft.com/en-us/free/students/)**
2. Click **"Start free"**
3. Sign in with your **college Microsoft account** (or create one with college email)
4. Microsoft verifies your student status automatically
5. You receive:
   - ✅ **$100 free credit** (valid 12 months)
   - ✅ **65+ always-free services** (including App Service F1)
   - ✅ **No credit card — ever**

> 💡 If you don't have a Microsoft account with your college email, go to [outlook.com](https://outlook.com) → create account → use your college email as an alias.

---

## PHASE 2 — Create the Backend on Azure (10 minutes)

### 2.1 Create the App Service

1. Go to **[portal.azure.com](https://portal.azure.com)**
2. In the search bar at the top, type **"App Services"** → click it
3. Click **"+ Create"** → **"Web App"**
4. Fill in the form:

   | Field | Value |
   |---|---|
   | **Subscription** | Azure for Students |
   | **Resource Group** | Click "Create new" → name it `ecobridge-rg` |
   | **Name** | `ecobridge-api` *(must be globally unique — try `ecobridge-api-2026`)* |
   | **Publish** | Code |
   | **Runtime stack** | Python 3.11 |
   | **Operating System** | Linux |
   | **Region** | Central India *(or South India — closest to you)* |
   | **Pricing plan** | Click "Explore pricing plans" → select **F1 (Free)** |

5. Click **"Review + create"** → **"Create"**
6. Wait ~2 minutes for deployment to finish
7. Click **"Go to resource"**

---

### 2.2 Configure Environment Variables

1. In your App Service page, click **"Configuration"** in the left sidebar
2. Under **"Application settings"**, click **"+ New application setting"** for each row below:

   | Name | Value |
   |---|---|
   | `DATABASE_URL` | `sqlite+aiosqlite:////home/site/wwwroot/data/ecobridge.db` |
   | `DEMO_MODE` | `true` |
   | `SECRET_KEY` | `ecobridge2026sih26229hackathonkey!!` |
   | `CORS_ORIGINS` | `*` |
   | `ACCESS_TOKEN_EXPIRE_MINUTES` | `10080` |
   | `PYTHONPATH` | `/home/site/wwwroot` |
   | `SCM_DO_BUILD_DURING_DEPLOYMENT` | `true` |

3. Click **"Save"** at the top → click **"Continue"** to confirm restart

---

### 2.3 Set the Startup Command

1. Still in **"Configuration"**, click the **"General settings"** tab
2. Find **"Startup Command"** field, paste:
   ```
   bash startup.sh
   ```
3. Click **"Save"**

---

### 2.4 Connect GitHub for Auto-Deploy

1. In the left sidebar, click **"Deployment Center"**
2. Under **Source**, select **"GitHub"**
3. Click **"Authorize"** → authorize Azure to access your GitHub
4. Fill in:

   | Field | Value |
   |---|---|
   | **Organization** | `atharvashivdikar01-stack` |
   | **Repository** | `Ecobridge` |
   | **Branch** | `main` |

5. Under **"Authentication type"**, keep **"User-assigned identity"**
6. Click **"Save"**

Azure will now:
- Auto-detect the Python app in the `backend/` folder
- Install `requirements.txt` automatically
- Run `startup.sh` on every push to `main`

---

### 2.5 Trigger First Deployment

1. In the left sidebar, click **"Deployment Center"** → **"Logs"** tab
2. You should see a deployment starting. Click on it to watch logs.
3. Wait for **"Success"** ✅ (takes 3–5 minutes)

### 2.6 Get Your Backend URL and Verify

1. Go back to the **"Overview"** tab of your App Service
2. Copy the **URL** — it looks like: `https://ecobridge-api-2026.azurewebsites.net`
3. **Verify** by opening in browser:
   ```
   https://ecobridge-api-2026.azurewebsites.net/docs
   ```
   → You should see the **Swagger UI** with all endpoints listed ✅

4. Test one endpoint:
   ```
   https://ecobridge-api-2026.azurewebsites.net/api/v1/materials/taxonomy
   ```
   → Should return 8 material categories in JSON ✅

> 📌 **COPY YOUR URL** — you'll need it for the next phase.

---

### 2.7 Get the Publish Profile (for GitHub Actions auto-deploy)

1. In your App Service **"Overview"** tab, click **"Download publish profile"**
2. Open the downloaded `.PublishSettings` file in Notepad
3. Copy **all the contents**
4. Go to your GitHub repo → **Settings** → **Secrets and variables** → **Actions**
5. Click **"New repository secret"**:
   - **Name:** `AZURE_PUBLISH_PROFILE`
   - **Value:** paste the entire file contents
6. Add another secret:
   - **Name:** `AZURE_APP_NAME`
   - **Value:** `ecobridge-api-2026` *(your app name)*

> Now every push to `main` will auto-deploy to Azure ✅

---

## PHASE 3 — Deploy Recycler Portal to Vercel (5 minutes)

1. Open **[vercel.com](https://vercel.com)** → **"Sign Up"** → **"Continue with GitHub"**
   *(No credit card — ever)*

2. Click **"Add New…"** → **"Project"**

3. Find `atharvashivdikar01-stack/Ecobridge` → click **"Import"**

4. Configure:

   | Setting | Value |
   |---|---|
   | **Project Name** | `ecobridge-recycler-portal` |
   | **Framework Preset** | Next.js *(auto-detected)* |
   | **Root Directory** | Click **"Edit"** → type `recycler_portal` → **"Continue"** |

5. Expand **"Environment Variables"** → add:

   | Name | Value |
   |---|---|
   | `NEXT_PUBLIC_API_URL` | `https://ecobridge-api-2026.azurewebsites.net` |

6. Click **"Deploy"** → wait ~60 seconds

7. ✅ Your URL: `https://ecobridge-recycler-portal.vercel.app`

**Verify:** Open URL → login with `+919811111111` / OTP `123456` → should reach dashboard ✅

---

## PHASE 4 — Deploy Admin Dashboard to Vercel (3 minutes)

1. In Vercel → **"Add New…"** → **"Project"**
2. Import the **same repository** again
3. Configure:

   | Setting | Value |
   |---|---|
   | **Project Name** | `ecobridge-admin-dashboard` |
   | **Framework Preset** | Next.js |
   | **Root Directory** | `admin_dashboard` |

4. Environment Variable:

   | Name | Value |
   |---|---|
   | `NEXT_PUBLIC_API_URL` | `https://ecobridge-api-2026.azurewebsites.net` |

5. Click **"Deploy"**

6. ✅ Your URL: `https://ecobridge-admin-dashboard.vercel.app`

**Verify:** Open URL → see the CPCB Admin Panel with demo banner ✅

---

## PHASE 5 — Android APK (Already Live)

The APK is already attached to the GitHub repository.

**Direct download link for judges:**
```
https://github.com/atharvashivdikar01-stack/Ecobridge/raw/main/release/EcoBridge-Collector-v1.0.apk
```

**To install:**
1. Open link on Android phone
2. Download → tap the `.apk` file
3. If prompted → Settings → Security → Enable "Unknown Sources" → Install
4. Open EcoBridge app → login with `+919811111111` / `123456`

---

## PHASE 6 — Update README with Live URLs

Once all three are live, update your README:

```powershell
cd C:\Users\admin\Downloads\Ecobridge-repo
# Edit README.md — replace placeholder URLs with your actual live URLs
git add README.md
git commit -m "docs: add live Azure + Vercel deployment URLs"
git push origin main
```

---

## Final Verification Checklist

Run through this before sharing with judges:

- [ ] `https://ecobridge-api-2026.azurewebsites.net/docs` → Swagger UI loads
- [ ] `https://ecobridge-api-2026.azurewebsites.net/api/v1/materials/taxonomy` → returns 8 categories
- [ ] Recycler Portal → login `+919811111111` / `123456` → dashboard loads
- [ ] Admin Dashboard → loads with illustrative demo banner
- [ ] APK installs on Android and logs in successfully
- [ ] Refresh backend after 10 min → **still up** (Azure F1 never sleeps ✅)

---

## Judge Information Card

```
╔══════════════════════════════════════════════════════════╗
║        ECOBRIDGE — SIH 2026 | PS 26229                  ║
╠══════════════════════════════════════════════════════════╣
║  🌐 Recycler Portal:                                     ║
║     https://ecobridge-recycler-portal.vercel.app         ║
║                                                          ║
║  📊 CPCB Admin Dashboard:                               ║
║     https://ecobridge-admin-dashboard.vercel.app         ║
║                                                          ║
║  ⚡ API (Swagger Docs):                                  ║
║     https://ecobridge-api-2026.azurewebsites.net/docs    ║
║                                                          ║
║  📱 Android APK:                                         ║
║     github.com/…/raw/main/release/EcoBridge-…apk        ║
║                                                          ║
║  DEMO LOGIN:  +919811111111  |  OTP: 123456              ║
╚══════════════════════════════════════════════════════════╝
```

---

## Troubleshooting

| Problem | Fix |
|---|---|
| Azure build fails: "No module named src" | Check `PYTHONPATH` env var is set to `/home/site/wwwroot` |
| 500 error on first request | `alembic upgrade head` may have failed — check Deployment Logs |
| Vercel: blank page | Verify `NEXT_PUBLIC_API_URL` has **no trailing slash** |
| OTP `123456` rejected | Verify `DEMO_MODE=true` is set in Azure Configuration |
| APK won't install | Enable "Install from Unknown Sources" in Android Settings |
| Azure app shows "Application Error" | Go to App Service → Log stream → read the error |
| Startup.sh permission denied | Azure auto-handles this — if it persists, check line endings (must be LF not CRLF) |
