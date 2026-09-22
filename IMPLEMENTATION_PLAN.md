# ECOBRIDGE Repository Restructuring Implementation Plan

## Overview
This plan outlines the steps to complete the repository restructuring to align with the agreed-upon tech stack (FastAPI + Next.js + pnpm + Turborepo monorepo) and integrate the contributor's work from ecobridgeee while preserving valuable existing code where possible.

## Current State Analysis
The main repo (Ecobridge-repo) already has:
- Basic monorepo structure with packages/ directory
- Backend migrated to FastAPI structure (backend/src/...)
- Recycler portal Next.js structure
- Configuration files partially updated
- Missing i18n package content
- Duplicate files and legacy Flask artifacts needing cleanup

## Implementation Strategy
Instead of blindly deleting files, we will:
1. **Convert where valuable**: Migrate useful logic from legacy files to new stack
2. **Clean up safely**: Remove only confirmed duplicates and obsolete artifacts
3. **Fill gaps**: Add missing components (especially i18n translations)
4. **Verify integrity**: Ensure all tests pass and imports work correctly

## Phase-by-Phase Implementation

### Phase 1: Preserve & Convert Valuable Legacy Code
**Target**: backend/app.py (Flask prototype)
- **Analysis**: This is a working health check and categories endpoint
- **Action**:
  - Extract the categories query logic
  - Convert to FastAPI endpoint in backend/src/api/v1/endpoints/
  - Preserve the multilingual category display functionality
  - Keep health check pattern but adapt to FastAPI
- **Files to create/modify**:
  - backend/src/api/v1/endpoints/health.py (new)
  - Enhance existing categories endpoint if needed

### Phase 2: Complete i18n Package
**Target**: packages/i18n/ (missing translation content)
- **Analysis**: Package structure exists but missing actual translations
- **Action**:
  - Create packages/i18n/src/locales/en.json with base UI strings
  - Create packages/i18n/src/locales/mr.json with Marathi translations
  - Create packages/i18n/src/locales/hi.json with Hindi translations
  - Create packages/i18n/src/index.ts with t(key, locale) utility function
- **Translation categories** (from plan):
  - Navigation: Dashboard, Materials, Handover, Payment, Ledger
  - Status labels: Collected, Offered, In Transit, Delivered, Completed
  - Lot fields: Weight, Price, Material, Category, Collector, Hazard
  - Auth: Login, OTP, Verify, Sign Out
  - Hazard warnings: Swollen Battery, Broken CRT, Burnt PCB safety alerts
  - Common UI: Search, Filter, Refresh, Reset, Submit

### Phase 3: Safe Cleanup of Confirmed Duplicates & Obsolete Artifacts
**Target**: Files marked for deletion in contributor's plan
- **Safe to delete** (confirmed duplicates/obsolete):
  - package (5).json, package (6).json (duplicates)
  - base (1).json (duplicate)
  - turbo (1).json (duplicate)
  - copilot-instructions (1).md (duplicate)
  - README (3-9).md, (15).md, (16).md, (14).md (duplicates)
  - ecobridge_dev.db (SQLite dev DB - never version control)
  - __init__ (3).py (duplicate)
- **Legacy backend artifacts to remove** (replaced by FastAPI structure):
  - backend/app.py (after converting useful parts)
  - backend/requirements.txt (Flask deps replaced)
  - backend/.env (contains old Flask database URL)
  - backend/venv/ (virtual environment)
  - backend/__pycache__/ (compiled bytecode)

### Phase 4: Update Configuration Files
**Target**: Incomplete config updates
- **README.md**: Replace with contributor's comprehensive README (README (13).md)
- **.gitignore**: Add Node.js/pnpm/Next.js/Turborepo specifics:
  ```
  # Node.js / pnpm / Turborepo (additional)
  .turbo/
  dist/
  .next/
  out/
  ```
  (Note: Some already exist, verify completeness)

### Phase 5: Verification & Testing
**Target**: Ensure everything works after changes
- **Backend tests**:
  ```bash
  cd backend && python -m pytest tests/ -v
  ```
- **Frontend build**:
  ```bash
  cd recycler_portal && npx next build
  ```
- **Monorepo lint/build**:
  ```bash
  pnpm run build
  pnpm run lint
  ```

## Decision Matrix: Convert vs Delete

| File/Pattern | Action | Reasoning |
|--------------|--------|-----------|
| backend/app.py | **Convert** | Contains useful health check and categories logic; extract to FastAPI |
| backend/requirements.txt | **Delete** | Fully replaced by FastAPI dependencies in pyproject.toml or similar |
| backend/.env | **Delete** | Contains outdated Flask DB URL; will be replaced by proper env setup |
| backend/venv/ | **Delete** | Virtual environment - never version controlled |
| backend/__pycache__/ | **Delete** | Compiled Python bytecode - rebuild as needed |
| Duplicate JSON/package files | **Delete** | Exact duplicates serve no purpose |
| Duplicate READMEs | **Delete** | Redundant documentation |
| ecobridge_dev.db | **Delete** | Development SQLite DB - never version control |
| i18n missing files | **Create** | Essential for i18n functionality |
| README.md | **Replace** | Contributor's version is more comprehensive |
| .gitignore | **Update** | Add missing Node.js/pnpm specifics |

## Estimated Effort
- Phase 1 (Convert legacy): 2-3 hours
- Phase 2 (Complete i18n): 3-4 hours (translation work)
- Phase 3 (Cleanup): 1 hour (safe deletions)
- Phase 4 (Config updates): 30 minutes
- Phase 5 (Verification): 1-2 hours
- **Total**: 7-10 hours

## Risks & Mitigations
1. **Risk**: Breaking existing functionality during conversion
   **Mitigation**: Extract logic carefully, run tests after each change

2. **Risk**: Missing translations in i18n
   **Mitigation**: Start with English base, then add Marathi/Hindi

3. **Risk**: Accidentally deleting non-duplicate files
   **Mitigation**: Verify duplicates with diff/checksum before deletion

## Success Criteria
- [ ] All duplicate files removed
- [ ] Legacy Flask artifacts cleaned up (after conversion)
- [ ] i18n package fully functional with all locales
- [ ] README.md updated with comprehensive documentation
- [ ] .gitignore properly configured for monorepo
- [ ] All backend tests pass
- [ ] Frontend builds successfully
- [ ] No import/path errors in monorepo
- [ ] Valuable logic from legacy files preserved in new stack

## Notes for Future AI Agents
This repository is now organized as a Turborepo monorepo with pnpm workspaces. Key conventions:
- Backend: Python/FastAPI in backend/src/
- Frontend: Next.js apps in recycler_portal/, admin_dashboard/, collector_app/
- Shared packages: @ecobridge/* in packages/
- Infrastructure: infra/ (docker, k8s, terraform)
- Scripts: scripts/ for automation
- Never hardcode UI text - use @ecobridge/i18n translation tokens
- All API contracts in @ecobridge/api-contracts
- Offline-first principles apply to mobile/web clients

---
*Plan created: 2026-09-22*