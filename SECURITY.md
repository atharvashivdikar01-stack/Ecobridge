# Security policy

## Supported scope

Security reports are currently accepted for the active FastAPI backend,
recycler portal, shared packages, dataset validation tooling, and CI
configuration on the default branch.

## Reporting a vulnerability

Please use GitHub's private
[security advisory reporting form](https://github.com/atharvashivdikar01-stack/Ecobridge/security/advisories/new).
Do not open a public issue or include credentials, personal data, or private
production records in a report.

Include the affected path, a concise description, reproduction steps or a
minimal proof of concept, impact, and any suggested mitigation. Redact
secrets from logs and attachments.

## Response expectations

We will acknowledge receipt when the report is triaged, keep the report
private while a fix is prepared, and coordinate disclosure after a fix or
mitigation is available. Timelines depend on severity and the ability to
reproduce the report.

## Safe development

Use the `.env.example` files as templates only. Store local values in ignored
`.env` or `.env.local` files, rotate any accidentally exposed credential
immediately, and never use production data in local tests or fixtures.
