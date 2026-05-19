# Incident Runbooks

These runbooks are written for local repo-based operation of the API from `D:\CAW sp`. Commands are PowerShell-first and copy-pasteable.

## Runbook: Database dependency unavailable

### Alert / Detection

- Alert name: `api-db-dependency-unavailable`
- Symptoms:
  - User-facing requests to DB-backed routes return `503 Service Unavailable` or `500 Internal Server Error`
  - Redirects may fail instead of returning `302` or `404`
  - Error logs show `dependency_timeout` or a DB-driver/import traceback
- How you know this is happening:
  - `curl.exe -i http://127.0.0.1:8000/r/test123` returns `503 Service Unavailable` or `500 Internal Server Error`
  - `Get-Content apps/api/uvicorn.err.log -Tail 50` shows `dependency_timeout` or `ModuleNotFoundError: No module named 'psycopg2'`

### Diagnosis

Run these commands in order.

**Step 1: Check the process liveness endpoint**

```powershell
curl.exe -i http://127.0.0.1:8000/health
```

- If this IS the problem, you will see:
  - `HTTP/1.1 200 OK`
  - `{"ok":true}`
- If this is NOT the problem, you will also see:
  - `HTTP/1.1 200 OK`
  - `{"ok":true}`

This step only proves the process is alive. It does not prove the database is reachable.

**Step 2: Check a DB-backed route**

```powershell
curl.exe -i http://127.0.0.1:8000/r/test123
```

- If this IS the problem, you will see:
  - `HTTP/1.1 503 Service Unavailable` with a JSON error envelope containing `"code":"dependency_unavailable"`
  - Or `HTTP/1.1 500 Internal Server Error` if the configured database driver is missing or the URL is malformed before the dependency wrapper can run
- If this is NOT the problem, you will see one of:
  - `HTTP/1.1 404 Not Found` with `"Link not found"` if the code does not exist
  - `HTTP/1.1 302 Found` if the code exists

**Step 3: Check the API error log**

```powershell
Get-Content apps/api/uvicorn.err.log -Tail 50
```

- If this IS the problem, you will see:
  - One or more lines containing `ERROR api-service dependency_timeout`
  - Or a traceback ending with `ModuleNotFoundError: No module named 'psycopg2'`
- If this is NOT the problem, you will see:
  - No recent `dependency_timeout` lines and no database-driver traceback for the failed request window

**Step 4: If process-inspection commands are blocked, switch to low-permission target discovery**

Use this branch when commands like `Get-CimInstance Win32_Process` or `tasklist` fail with `Access denied`.

```powershell
curl.exe -i http://127.0.0.1:8000/health
netstat -ano | findstr :8000
Get-Content apps/api/uvicorn.err.log -Tail 50
```

- If this IS the problem, you will see one or more of:
  - `curl: (7) Failed to connect to localhost port 8000`
  - No `netstat` listener on `:8000`
  - Old or empty log output that does not match a currently running API
- If this is NOT the problem, you will see:
  - `HTTP/1.1 200 OK` from `/health`
  - A live listener on `:8000`
  - Recent request log lines for the current incident window

**Step 5: Confirm the current database URL**

```powershell
Get-Content apps/api/.env | Select-String "^DATABASE_URL="
```

- If this IS the problem, you may see:
  - An empty value
  - A clearly incorrect host or port
- If this is NOT the problem, you will see:
  - A valid SQLAlchemy URL string for the intended database

### Fix

Follow these steps in order. Do not skip steps.

**Step 1: Correct the database configuration**

Edit `apps/api/.env` and set `DATABASE_URL` to the known-good value for the environment.

Then confirm the change:

```powershell
Get-Content apps/api/.env | Select-String "^DATABASE_URL="
```

- Expected output:
  - A non-empty `DATABASE_URL=...` line
- If this does NOT produce the expected output, go to Escalation.

**Step 2: If the log shows a missing PostgreSQL driver, revert to the known-good SQLite URL or install the required driver before restarting**

```powershell
Get-Content apps/api/uvicorn.err.log -Tail 80 | Select-String 'ModuleNotFoundError: No module named ''psycopg2'''
```

- Expected output:
  - Either no matches, or a line confirming the missing-driver failure mode

For the local repo drill, the known-good recovery value is:

```powershell
(Get-Content apps/api/.env) -replace '^DATABASE_URL=.*$', 'DATABASE_URL=sqlite:///./runbook-test-good.db' | Set-Content apps/api/.env
```

Then confirm the change:

```powershell
Get-Content apps/api/.env | Select-String "^DATABASE_URL="
```

- Expected output:
  - `DATABASE_URL=sqlite:///./runbook-test-good.db`

**Step 3: Stop the current API process**

```powershell
Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*uvicorn app.main:app*--port 8000*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }
```

- Expected output:
  - No error output

**Step 4: Start the API with the repo env file**

```powershell
$env:APP_ENV='development'; $env:SERVICE_NAME='api-service'; $env:PORT='8000'; $env:JWT_SECRET='dev-secret'; $env:API_KEY_A='local-key-a'; $env:API_KEY_B='local-key-b'; $env:CORS_ORIGIN='http://localhost:3000'; Get-Content apps/api/.env | ForEach-Object { if ($_ -match '^([^#=]+)=(.*)$') { [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process') } }; Start-Process -FilePath 'D:\CAW sp\apps\api\.venv\Scripts\python.exe' -ArgumentList '-m','uvicorn','app.main:app','--host','127.0.0.1','--port','8000' -WorkingDirectory 'D:\CAW sp\apps\api' -WindowStyle Hidden -RedirectStandardOutput 'D:\CAW sp\apps\api\uvicorn.out.log' -RedirectStandardError 'D:\CAW sp\apps\api\uvicorn.err.log'
```

- Expected output:
  - No console error output

**Step 5: Wait for startup**

```powershell
Start-Sleep -Seconds 4; Get-Content apps/api/uvicorn.err.log -Tail 20
```

- Expected output:
  - `Application startup complete.`
  - `Uvicorn running on http://127.0.0.1:8000`

If you cannot confirm the API process directly because process-inspection commands are blocked, treat these as the required fallback startup checks:

```powershell
curl.exe -i http://127.0.0.1:8000/health
netstat -ano | findstr :8000
Get-Content apps/api/uvicorn.err.log -Tail 20
```

- Expected output:
  - `/health` returns `HTTP/1.1 200 OK`
  - `netstat` shows a listener on `:8000`
  - The log shows startup completion

### Verification

Confirm the fix worked:

```powershell
curl.exe -i http://127.0.0.1:8000/r/test123
```

- Expected output:
  - `HTTP/1.1 404 Not Found` or `HTTP/1.1 302 Found`
  - Not `503 Service Unavailable`

Wait 2 minutes and check again:

```powershell
Start-Sleep -Seconds 120; curl.exe -i http://127.0.0.1:8000/r/test123
```

- Expected output should be the same.

### Escalation

If this runbook does not resolve the issue within 10 minutes:

1. Post in `#api-oncall` with the exact commands you ran, the last 20 lines of `apps/api/uvicorn.err.log`, and timestamps.
2. Page the platform/on-call engineer through PagerDuty for the `api-service` service.
3. If there is no response in 10 minutes, call the engineering manager directly.

Do not spend more than 10 minutes debugging this alone at 3 AM.

## Runbook: High 5xx error rate

### Alert / Detection

- Alert name: `api-high-error-rate`
- Symptoms:
  - Multiple endpoints return `500 Internal Server Error`
  - Metrics show rising `http_requests_total` with `status_code="500"`
  - `uvicorn.err.log` contains `request failed` and `unhandled exception`
- How you know this is happening:
  - `curl.exe -i http://127.0.0.1:8000/health` still returns `200`, but business routes fail
  - Logs show `status_code=500`

### Diagnosis

**Step 1: Check if the process is up**

```powershell
curl.exe -i http://127.0.0.1:8000/health
```

- If this IS the problem, you will usually still see:
  - `HTTP/1.1 200 OK`
  - `{"ok":true}`
- If this is NOT the problem, you will also see:
  - `HTTP/1.1 200 OK`
  - `{"ok":true}`

**Step 2: Check recent 500s in metrics**

```powershell
curl.exe -s http://127.0.0.1:8000/metrics | Select-String 'http_requests_total.*status_code="500"'
```

- If this IS the problem, you will see:
  - At least one `http_requests_total{...,status_code="500"}` metric line
- If this is NOT the problem, you will see:
  - No matching lines

**Step 3: Check the error log**

```powershell
Get-Content apps/api/uvicorn.err.log -Tail 80
```

- If this IS the problem, you will see:
  - `ERROR api-service request failed`
  - `ERROR api-service unhandled exception`
- If this is NOT the problem, you will see:
  - No recent unhandled exception tracebacks

### Fix

**Step 1: Capture the failing traceback before restarting**

```powershell
Get-Content apps/api/uvicorn.err.log -Tail 120
```

- Expected output:
  - The current stack trace or error context is visible for handoff

**Step 2: Restart the API process**

```powershell
Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*uvicorn app.main:app*--port 8000*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }
Start-Sleep -Seconds 2
$env:APP_ENV='development'; $env:SERVICE_NAME='api-service'; $env:PORT='8000'; $env:JWT_SECRET='dev-secret'; $env:API_KEY_A='local-key-a'; $env:API_KEY_B='local-key-b'; $env:CORS_ORIGIN='http://localhost:3000'; Get-Content apps/api/.env | ForEach-Object { if ($_ -match '^([^#=]+)=(.*)$') { [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process') } }; Start-Process -FilePath 'D:\CAW sp\apps\api\.venv\Scripts\python.exe' -ArgumentList '-m','uvicorn','app.main:app','--host','127.0.0.1','--port','8000' -WorkingDirectory 'D:\CAW sp\apps\api' -WindowStyle Hidden -RedirectStandardOutput 'D:\CAW sp\apps\api\uvicorn.out.log' -RedirectStandardError 'D:\CAW sp\apps\api\uvicorn.err.log'
```

- Expected output:
  - No console error output

**Step 3: Confirm startup after restart**

```powershell
Start-Sleep -Seconds 4; Get-Content apps/api/uvicorn.err.log -Tail 20
```

- Expected output:
  - `Application startup complete.`

### Verification

```powershell
curl.exe -i http://127.0.0.1:8000/health
curl.exe -s http://127.0.0.1:8000/metrics | Select-String 'http_requests_total.*status_code="500"'
```

- Expected output:
  - `/health` returns `HTTP/1.1 200 OK`
  - No new burst of `status_code="500"` lines after the restart window

Wait 2 minutes and check again:

```powershell
Start-Sleep -Seconds 120; Get-Content apps/api/uvicorn.err.log -Tail 40
```

- Expected output should be:
  - No new unhandled exception burst for the same incident

### Escalation

If this runbook does not resolve the issue within 10 minutes:

1. Post in `#api-oncall` with the traceback, the failing route, and the restart timestamp.
2. Page the platform/on-call engineer through PagerDuty for the `api-service` service.
3. If 5xx errors continue after one restart, stop restarting and escalate to the engineering manager.

## Runbook: High latency / slow responses

### Alert / Detection

- Alert name: `api-high-latency`
- Symptoms:
  - Requests are slow but may still return `200`, `302`, or `404`
  - Metrics show `http_request_duration_seconds`
  - Logs show high `latency_ms`
- How you know this is happening:
  - `curl.exe` wall-clock time to a route rises above the normal baseline
  - Logs show repeated requests with multi-second `latency_ms`

### Diagnosis

**Step 1: Measure `/health` latency**

```powershell
curl.exe -o NUL -s -w "health_total=%{time_total}`n" http://127.0.0.1:8000/health
```

- If this IS the problem, you may see:
  - `health_total` well above the normal local baseline
- If this is NOT the problem, you will see:
  - `health_total` near the normal local baseline

**Step 2: Measure a DB-backed route**

```powershell
curl.exe -o NUL -s -w "redirect_total=%{time_total}`n" http://127.0.0.1:8000/r/test123
```

- If this IS the problem, you will see:
  - `redirect_total` in the multi-second range
- If this is NOT the problem, you will see:
  - `redirect_total` near the normal baseline or a fast `404`

**Step 3: Inspect latency logs**

```powershell
Get-Content apps/api/uvicorn.err.log -Tail 80
```

- If this IS the problem, you will see:
  - Recent request lines with very large `latency_ms`
  - Possible `dependency_timeout` lines if latency is caused by DB saturation
- If this is NOT the problem, you will see:
  - No recent high-latency lines

### Fix

**Step 1: If the log shows dependency timeouts, follow the Database dependency unavailable runbook**

```powershell
Get-Content apps/api/uvicorn.err.log -Tail 80 | Select-String 'dependency_timeout'
```

- Expected output:
  - Either matching `dependency_timeout` lines or no matches

**Step 2: Restart the API process to clear local saturation**

```powershell
Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*uvicorn app.main:app*--port 8000*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }
Start-Sleep -Seconds 2
$env:APP_ENV='development'; $env:SERVICE_NAME='api-service'; $env:PORT='8000'; $env:JWT_SECRET='dev-secret'; $env:API_KEY_A='local-key-a'; $env:API_KEY_B='local-key-b'; $env:CORS_ORIGIN='http://localhost:3000'; Get-Content apps/api/.env | ForEach-Object { if ($_ -match '^([^#=]+)=(.*)$') { [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process') } }; Start-Process -FilePath 'D:\CAW sp\apps\api\.venv\Scripts\python.exe' -ArgumentList '-m','uvicorn','app.main:app','--host','127.0.0.1','--port','8000' -WorkingDirectory 'D:\CAW sp\apps\api' -WindowStyle Hidden -RedirectStandardOutput 'D:\CAW sp\apps\api\uvicorn.out.log' -RedirectStandardError 'D:\CAW sp\apps\api\uvicorn.err.log'
```

- Expected output:
  - No console error output

### Verification

```powershell
Start-Sleep -Seconds 4
curl.exe -o NUL -s -w "health_total=%{time_total}`n" http://127.0.0.1:8000/health
curl.exe -o NUL -s -w "redirect_total=%{time_total}`n" http://127.0.0.1:8000/r/test123
```

- Expected output:
  - Lower wall-clock times than during the incident

Wait 2 minutes and check again:

```powershell
Start-Sleep -Seconds 120; Get-Content apps/api/uvicorn.err.log -Tail 40
```

- Expected output should be:
  - No continuing burst of multi-second request latency

### Escalation

If this runbook does not resolve the issue within 15 minutes:

1. Post the before/after latency numbers in `#api-oncall`.
2. Page the platform/on-call engineer through PagerDuty for the `api-service` service.
3. If latency remains high after one restart and no clear dependency timeout appears, escalate to the engineering manager for deeper capacity investigation.
