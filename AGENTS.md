# Repository Guidelines

## Project Structure & Module Organization
This repository is currently empty, so contributors should keep the initial layout simple and predictable. Place application code in `src/`, tests in `tests/`, static assets in `assets/`, and project documentation in `docs/`. Keep root-level files limited to repository metadata and tool configuration such as `README.md`, `.gitignore`, and formatter or linter configs.

Example layout:
```text
src/
tests/
assets/
docs/
```

## Build, Test, and Development Commands
No build system is configured yet. When introducing one, document the standard local workflow in `README.md` and keep commands consistent across contributors.

Recommended baseline commands:
- `npm install` or equivalent dependency restore command
- `npm run dev` for local development
- `npm test` for the default test suite
- `npm run lint` and `npm run format` for code quality

Only add commands that are wired into the repository and safe for other contributors to run.

## Coding Style & Naming Conventions
Use 4 spaces for indentation unless the chosen language ecosystem strongly prefers otherwise. Name files and directories consistently: `kebab-case` for frontend or config files, `snake_case` for Python modules, and `PascalCase` for class names. Keep functions small, prefer descriptive identifiers, and avoid adding multiple competing patterns in the first commit.

Adopt an automated formatter and linter as soon as the primary stack is chosen.

## Testing Guidelines
Put tests under `tests/` and mirror the structure of `src/`. Use names that make scope obvious, such as `tests/api/test_health.py` or `src/components/button.test.ts`. Add at least one automated test for each new feature or bug fix, and make sure the default test command runs cleanly before opening a PR.

## Commit & Pull Request Guidelines
Git history is not available in this workspace, so no repository-specific commit convention could be inferred. Use short, imperative commit messages such as `Add initial API scaffold` or `Fix login validation`.

For pull requests, include:
- a clear summary of the change
- linked issue or task ID when applicable
- test evidence
- screenshots for UI changes

## Security & Configuration Tips
Do not commit secrets, local environment files, or generated credentials. Keep sensitive values in ignored local config files such as `.env` and document required variables in `README.md`.
