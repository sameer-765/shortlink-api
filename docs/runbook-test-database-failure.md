# Runbook Test: Database Failure

Test date: `2026-05-09`

Tested runbook: `Database dependency unavailable`

## Simulated failure

Started the API on port `8017` with an unreachable PostgreSQL URL:

```powershell
$env:APP_ENV='development'
$env:SERVICE_NAME='api-service'
$env:PORT='8017'
$env:JWT_SECRET='dev-secret'
$env:API_KEY_A='local-key-a'
$env:API_KEY_B='local-key-b'
$env:CORS_ORIGIN='http://localhost:3000'
$env:DATABASE_URL='postgresql://user:pass@127.0.0.1:6543/runbookdb'
```

Then started uvicorn and hit the DB-backed redirect route four times:

```powershell
curl.exe -s -o NUL -w "attempt=1 code=%{http_code} total=%{time_total}`n" http://127.0.0.1:8017/r/test123
curl.exe -s -o NUL -w "attempt=2 code=%{http_code} total=%{time_total}`n" http://127.0.0.1:8017/r/test123
curl.exe -s -o NUL -w "attempt=3 code=%{http_code} total=%{time_total}`n" http://127.0.0.1:8017/r/test123
curl.exe -s -o NUL -w "attempt=4 code=%{http_code} total=%{time_total}`n" http://127.0.0.1:8017/r/test123
```

Observed output:

```text
attempt=1 code=500 total=0.074732
attempt=2 code=500 total=0.008899
attempt=3 code=500 total=0.016433
attempt=4 code=500 total=0.018191
```

Observed log evidence from `apps/api/runbook-test-bad.err.log`:

```text
ModuleNotFoundError: No module named 'psycopg2'
```

## Recovery

Stopped the bad process, changed the database URL to a known-good local SQLite value, and restarted the API:

```powershell
DATABASE_URL=sqlite:///./runbook-test-good.db
```

Verification commands:

```powershell
curl.exe -i http://127.0.0.1:8017/health
curl.exe -i http://127.0.0.1:8017/r/test123
```

Observed healthy-state evidence:

```text
HTTP/1.1 200 OK
{"ok":true}
```

```text
HTTP/1.1 404 Not Found
```

Observed log evidence from `apps/api/runbook-test-good.err.log`:

```text
INFO api-service request completed request_id=... route=/health method=GET status_code=200
INFO api-service request completed request_id=... route=/r/{code} method=GET status_code=404
```

## Fixes required after testing

The runbook needed `4` fixes after the simulated drill:

1. Added a `500 Internal Server Error` branch for missing DB drivers, because the local harness failed before reaching the `503 dependency_unavailable` path.
2. Added a log check for `ModuleNotFoundError: No module named 'psycopg2'` instead of assuming every DB outage would log only `dependency_timeout`.
3. Clarified that `/health` only proves the process is alive and cannot confirm database reachability.
4. Added a known-good local recovery value for `DATABASE_URL` so the restart path is executable in this repo without guessing.
