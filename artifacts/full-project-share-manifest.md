# Full Project Share Manifest

This is the clean set of project material that should be shared publicly when the repository is made public.

## Core Project Folders

- `.github/`
- `apps/api/app/`
- `apps/api/tests/`
- `apps/api/scripts/`
- `artifacts/`
- `docs/`
- `infra/`
- `ops/`
- `progress/`

## Root Files Worth Sharing

- `AGENTS.md`
- `CLAUDE.md`
- `upsk-report.json`
- `module8-report.json`

## Key Deliverables Already Present

- [module-06-interface-contracts.md](/D:/CAW%20sp/artifacts/contracts/module-06-interface-contracts.md)
- [incident-runbooks.md](/D:/CAW%20sp/docs/incident-runbooks.md)
- [service-overview.md](/D:/CAW%20sp/docs/service-overview.md)
- [verify-module-04.md](/D:/CAW%20sp/artifacts/verify-module-04.md)
- [module-08-integration-test-plan.md](/D:/CAW%20sp/artifacts/checklists/module-08-integration-test-plan.md)
- [module-08-traceability-matrix.md](/D:/CAW%20sp/artifacts/checklists/module-08-traceability-matrix.md)
- [ticket-index.md](/D:/CAW%20sp/artifacts/tickets/module-05/ticket-index.md)
- [full-project-share-manifest.md](/D:/CAW%20sp/artifacts/full-project-share-manifest.md)
- [share-status-2026-05-18.md](/D:/CAW%20sp/artifacts/share-status-2026-05-18.md)

## Files That Should Usually Stay Out Of A Public Repo

- `.venv/` and `apps/api/.venv/`
- `__pycache__/`
- local `.db` files
- `*.log`
- `tmp-*`
- backup binaries like `upsk.exe.bak`, `upsk.exe.old`, `upsk.exe.preupgrade.bak`
- machine-specific outputs such as `status_out.txt`, `report_out.txt`, and similar CLI dump files

## Why This Split Matters

- Public repos are easier to review when they contain source, docs, tests, and artifacts only.
- Local runtime files make the repo look unfinished and can expose noise or machine-specific state.
- If needed, those local files can still be zipped separately for private review, but they usually should not be the public face of the work.
