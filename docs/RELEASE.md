# Release checklist

EcoBridge does not currently publish versioned packages or deploy production
providers from this repository. A release is therefore a validated source
snapshot, not an automated production deployment.

## Prepare

1. Confirm the intended change is within the active repository scope:
   `backend`, `recycler_portal`, `packages/*`, or `datasets`.
2. Review the diff for credentials, personal data, generated output, and
   unsupported Android or provider integrations.
3. Update related documentation and shared contracts when behavior changes.

## Validate

Run the checks listed in [`CONTRIBUTING.md`](../CONTRIBUTING.md):

- backend compile and tests
- recycler portal typecheck, lint, and build
- dataset validation when datasets or validation code changed
- `git diff --check`

The same checks run in `.github/workflows/ci.yml` for pushes to `main` and
pull requests. The workflow also runs a Gitleaks repository scan.

## Approve and publish

Merge only after CI is green and required reviewers approve the pull request.
Create deployment configuration and provider-specific credentials separately;
this repository does not claim to provision those integrations.
