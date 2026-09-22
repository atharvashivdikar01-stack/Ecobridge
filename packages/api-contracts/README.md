# @ecobridge/api-contracts 📄

Shared contracts, TypeScript types, DTOs, and Zod schemas shared across `apps/collector-mobile`, `apps/recycler-portal`, `apps/admin-dashboard`, and `apps/api-server`.

## Key Responsibilities
- **API Payloads:** Strongly typed request/response shapes.
- **Zod Schemas:** Input validation schemas ensuring consistent validation on mobile, web, and server.
- **Enumerations:** Single source of truth for lot statuses, e-waste categories, and hazard levels.

Production boundary statuses such as `ProviderOperationStatus`, payment
confirmation shape, readiness checks, and the `Idempotency-Key` header constant
are also defined here. Client workstreams should import these types rather than
redeclaring provider or deployment behavior. Provider credentials and concrete
adapters remain server/deployment concerns.
