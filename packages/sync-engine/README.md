# @ecobridge/sync-engine 🔄

Offline-first delta synchronization protocol and conflict resolution engine shared between `apps/collector-mobile` and `apps/api-server`.

## Key Responsibilities
- **Mutation Queue:** Tracks pending inserts, updates, and deletes with monotonic versioning.
- **Delta Payloads:** Serializes and compresses change-sets for transmission over low-bandwidth 2G/EDGE networks.
- **Deterministic Conflict Resolution:** Executes rule-based resolution (client-wins for physical collection facts; server-wins for market pricing, approvals, and payouts).
