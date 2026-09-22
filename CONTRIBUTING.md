# Contributing to EcoBridge

## Before you start

Read [`AGENTS.md`](AGENTS.md) for the repository invariants and ownership
boundaries. Do not commit `.env` files, credentials, personal data, generated
build output, or production records. Use the private reporting path in
[`SECURITY.md`](SECURITY.md) for vulnerabilities.

The active checked-in applications are `backend` (FastAPI) and
`recycler_portal` (Next.js). The declared pnpm workspace also contains
`packages/*`. The collector app and the `apps/*` tree are placeholders or
separate scaffolding and are not part of the default CI build.

## Local checks

Backend:

```bash
python -m pip install -r backend/requirements.txt
python -m compileall -q backend/src backend/tests
```

On Windows:

```powershell
$env:PYTHONPATH = "backend"
python -m pytest backend/tests -q
```

On macOS/Linux, use `PYTHONPATH=backend python -m pytest backend/tests -q`.

Frontend and workspace:

```bash
pnpm install
pnpm --dir recycler_portal exec tsc --noEmit
pnpm lint
pnpm build
```

If you change tracked datasets, also run:

```bash
python datasets/scripts/validate_datasets.py
```

## Pull requests

Keep changes focused, describe behavior and limitations, and include the
commands used for validation. Update directly related documentation and shared
contracts. Do not add Android implementation or production provider
integrations as part of unrelated changes.
