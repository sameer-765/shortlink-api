## Trust Audit Format

- Confirmed: verified directly in code/tests and matches the agent claim
- Needs Verification: plausible, but not yet proven from the codebase
- Suspicious: confident claim with missing evidence, contradictions, or security risk signs

## Initial Assessment

### Confirmed

- Route inventory and folder structure
  - Easy to verify directly from router registration and file layout.

### Needs Verification

- Ownership enforcement through `Link.created_by == principal_id`
  - This is security-sensitive and should be proven from query logic and tests, not just accepted from the summary.

### Suspicious

- `JWT_SECRET` being listed as important configuration while the active authentication flow is described as API-key only
  - This may be unused, legacy, or misleading context and should not be treated as active auth behavior without proof in code paths.

## Verification Commands And Results

- Command:
  `POST /links` without an `X-API-Key` header using the app test client
- Result:
  Returned `401`
- Response body:
  `{"error":{"code":"unauthorized","message":"Missing X-API-Key header","request_id":"..."}}`
- Conclusion:
  This confirms protected route behavior rejects missing API keys and supports the summary claim that shared API-key auth is actively enforced on protected link routes.

- Command:
  `rg "require_principal_id|X-API-Key|Authorization|Bearer|jwt|JWT" app`
- Result:
  `jwt_secret` appears in `app/config.py`, but protected route wiring points to `require_principal_id` in `app/dependencies/auth.py`, and the dependency reads `X-API-Key`.
- Conclusion:
  This supports the suspicion that `JWT_SECRET` is currently unused or legacy configuration rather than active request authentication for protected routes.

## Break Step Wrong-Claim Check

Claim said: This starter workspace has no packages directory; all runtime code is under a single top-level src/ folder.

Verification commands:
- `Get-ChildItem` at workspace root `D:\CAW sp`
- `Get-ChildItem packages` at workspace root `D:\CAW sp`

Observed:
- The workspace root contains an `apps/` directory and does not contain a top-level `src/` directory.
- `Get-ChildItem packages` failed because `D:\CAW sp\packages` does not exist.

Corrected:
- This workspace does not use a single top-level `src/` runtime layout.
- The connected application runtime code lives under `apps/api/app`, and there is no `packages/` directory at the workspace root.
