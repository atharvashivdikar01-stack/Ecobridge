# API contract notes

The FastAPI schemas under `apps/api-server/src/schemas` are the current
implementation source for API payloads. Android and AI clients should consume
the documented route shapes and the shared response envelope rather than
copying Python DTO implementations.

Authentication uses:

* `POST /api/v1/auth/otp/send` — returns phone, an operator-safe message, and
  expiry seconds; it never returns an OTP.
* `POST /api/v1/auth/otp/verify` — consumes a one-time code and returns bearer
  access/refresh tokens.

Mutating offline-sync requests must eventually provide an `Idempotency-Key`;
clients should reuse the same key for retries and never reuse it for a
different payload. Payment confirmation does not imply money moved: clients
must inspect `status`, `provider_configured`, and nullable `txn_reference`.
`PENDING_PROVIDER_CONFIGURATION` is an explicit development/non-live result.

All responses use `{success, data, error, timestamp}`. Generated client
types, if added, belong in the repository's shared API-contract package;
this document intentionally does not duplicate DTO definitions.
