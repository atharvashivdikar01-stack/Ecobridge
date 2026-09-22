# infra/k8s ☸️

Production Kubernetes manifests and Helm charts for deploying ECOBRIDGE services.

## Architecture
- **API Server:** Horizontal Pod Autoscaler (HPA) targeting 70% CPU/Memory utilization.
- **Web Applications:** Node SSR pods fronted by NGINX Ingress Controller with TLS termination.
- **Workers:** BullMQ consumers for background sync processing and market price scrapers.

## API operational requirements

The FastAPI service exposes `/api/v1/health/liveness` for process liveness and
`/api/v1/health/readiness` for dependency readiness. A readiness response is
HTTP 503 until PostgreSQL is reachable; Kubernetes should remove the pod from
service rather than restart it for that condition.

For staging and production, set `ENVIRONMENT`, `DEBUG=false`, a randomly
generated `JWT_SECRET_KEY` (at least 32 characters), non-local
`DATABASE_URL`/`REDIS_URL`, and an empty `TEST_OTP`. Provider credentials are
deployment secrets, not repository configuration. The development OTP,
in-memory idempotency store, and development provider ports are intentionally
not live integrations and must not be used for customer traffic.

Mutating clients should send an `Idempotency-Key`. Implementations must persist
the request fingerprint and response in a transactional store (the bundled
in-memory helper is for development/tests only). Webhook handlers must verify
the raw body, timestamp, and provider signature before accepting an event and
deduplicate provider event IDs.
