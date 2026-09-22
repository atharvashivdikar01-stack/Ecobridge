# @ecobridge/api-server ⚙️

The **API Server** provides core backend microservices for the ECOBRIDGE platform, written in TypeScript with Fastify/NestJS.

## Key Capabilities
- **Authentication & RBAC:** Phone OTP issuance, JWT validation, and multi-role access control.
- **Delta Sync Endpoint:** Ingests offline batch mutations with strict idempotency and conflict resolution.
- **Fair-Price Intelligence Engine:** Scrapes and normalizes commodity scrap market prices (LME, domestic markets).
- **Lot Lifecycle State Machine:** Enforces valid transitions from initial draft through recycler intake and final settlement.
- **Payout & Escrow Service:** Coordinates instant transfers via UPI/IMPS rails and maintains double-entry accounting ledgers.

## Development
```bash
# Start server in watch mode
pnpm --filter @ecobridge/api-server dev

# Build production bundle
pnpm --filter @ecobridge/api-server build
```
