# API production-readiness checklist

`apps/api-server` keeps the existing API response envelope and development
defaults, while making unsafe deployment configuration fail fast.

## Configuration

Use `ENVIRONMENT=staging` or `production` only with `DEBUG=false`, a unique
32+ character `JWT_SECRET_KEY`, non-local database/Redis URLs, and no
`TEST_OTP`. JWTs are restricted to HS256/384/512 and include issuer/audience
claims. Never log OTP values or put provider secrets in source control.

## Providers and mutations

`src/core/providers.py` defines narrow OTP, payment, and object-storage ports.
The development implementations raise `ProviderUnavailable`; they do not send
messages, charge money, or claim to have stored files. Replace them with
explicitly configured adapters before enabling live traffic.

Use `src/core/idempotency.py` for mutating requests. The in-memory store is
only a local fallback; production adapters must atomically reserve a key,
compare the actor-bound request fingerprint, and replay the saved response.
Use `src/core/webhooks.py` to validate the raw body and timestamped HMAC before
parsing a webhook. Persist event IDs to prevent replay.

## Probes

* `/api/v1/health/liveness` checks only that the process is alive.
* `/api/v1/health/readiness` checks required PostgreSQL connectivity and returns
  HTTP 503 when unavailable.

## Database migrations and recovery

The API currently carries `alembic.ini`, but this checkout has no committed
application revision under `apps/api-server/alembic/versions`. The shared
database package does contain a Prisma schema and migration, but it is not an
automatic substitute for an API Alembic revision. Treat the API migration
history as unverified until an operator confirms the deployed database's
`alembic_version` table and migration source revision, and records which
migration system owns each release.

Before every release:

1. Take a PostgreSQL logical backup (`pg_dump --format=custom`) and verify it
   can be listed with `pg_restore --list`.
2. Run `alembic current`, `alembic heads`, and `alembic check` against the
   release database using the release source tree.
3. Apply only forward migrations with `alembic upgrade head`; never edit an
   applied revision. Record the output and resulting revision.
4. Test restore into an isolated database with `pg_restore`, then run the
   API readiness and smoke tests before promotion.

Rollback means restoring the tested backup or deploying a forward corrective
migration; do not downgrade production in place without an approved recovery
plan.

## Deployment and monitoring

Run at least two API replicas behind TLS termination. Configure liveness and
readiness probes as described above, alert on readiness failures, 5xx rate,
latency, database pool exhaustion, OTP verification failures, and provider
unavailability. Logs must exclude OTPs, access tokens, payment credentials,
and request bodies containing personal data. Retain structured logs and
correlation IDs according to the organization's privacy policy.

Backups should be encrypted, access-controlled, tested regularly, and retained
according to recovery-point/recovery-time objectives. Monitor backup age and
restore-test success, not only backup job completion.
