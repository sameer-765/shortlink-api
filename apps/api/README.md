# API

## Local Setup

Copy `.env.example` to `.env`, then fill in local values for `DATABASE_URL`, `API_KEY_A`, `API_KEY_B`, and any other settings your machine needs before starting the API or running tests.

## Authorization Rules for Mutating Endpoints

- Every create, update, or delete endpoint must verify the authenticated user's team role or resource ownership server-side before mutation.
- Return `401` for unauthenticated requests.
- Return `403` for authenticated users who are not authorized for the exact team or resource.
- Cross-team access must always be blocked.
- Denied requests must not change database state.
- Denied requests must not emit audit or activity events.
- Never trust client-provided team IDs or roles without server-side verification.
- Every new mutating endpoint must include regression tests for both success and denial paths before merge.

## Focused Auth Regression Gate

Run the production auth gate from `apps/api`:

```powershell
..\..\.venv\Scripts\python.exe -m unittest tests.test_invitations tests.test_comments tests.test_audit_events
```

CI enforces the same gate through [`scripts/run_auth_ci.ps1`](scripts/run_auth_ci.ps1), which fails on test failures, skipped tests, or missing auth test modules.
