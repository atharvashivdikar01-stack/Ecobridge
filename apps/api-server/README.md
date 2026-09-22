# @ecobridge/api-server ⚙️

The **API Server** provides core backend services for the ECOBRIDGE platform,
implemented with FastAPI, SQLAlchemy async, and PostgreSQL-compatible schemas.

## Key Capabilities
- **Authentication & RBAC:** Phone OTP issuance, JWT validation, and multi-role access control.
- **Delta Sync Endpoint:** Ingests offline batch mutations with strict idempotency and conflict resolution.
- **Fair-Price Intelligence Engine:** Scrapes and normalizes commodity scrap market prices (LME, domestic markets).
- **Lot Lifecycle State Machine:** Enforces valid transitions from initial draft through recycler intake and final settlement.
- **Payout & Escrow Boundary:** Exposes a provider-neutral payment port; live
  payment adapters and credentials are deployment-owned.

## Development
```bash
# Start server in development
PYTHONPATH=. uvicorn src.main:app --reload --port 8000

# Run backend tests from the repository root
PYTHONPATH=apps/api-server pytest apps/api-server/tests -q
```

Production configuration, migration verification, backups, probes, and
provider-boundary requirements are documented in
[`docs/API_OPERATIONS.md`](../../docs/API_OPERATIONS.md).
