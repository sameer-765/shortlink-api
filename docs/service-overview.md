# Service Overview

## Purpose

This API provides link management, redirects, teams, invitations, comments, and basic analytics. It should keep non-critical features degraded when possible, but fail closed for auth, protected data, and database-backed writes.

## Dependencies

| Dependency | Used for | Fallback behavior |
|---|---|---|
| SQL database | Core reads/writes, links, teams, comments, analytics | Fail fast with 503 if unavailable |
| Redis / Celery | Optional async click-event processing | Fail open where possible; process synchronously or skip non-critical async work |
| DNS / network | Resolving database/cache hosts | Fail fast with clear dependency logs |
| File system | Local runtime files/logs if used | Preserve read paths where possible; alert on disk issues |
| CPU / memory | Running API process | Restart via container/process manager; alert on saturation |
| Prometheus scraper | Metrics collection from `/metrics` | App keeps serving; observability is degraded |

## Endpoints

- `GET /health` - liveness check
- `GET /ready` - readiness check
- `GET /metrics` - Prometheus metrics
- `/links/*` - link management
- `/r/{code}` - redirect path
- `/teams/*` - team operations
- `/invitations/*` - invitation operations
- `/comments/*` - comment operations

## Configuration

Reference file: `apps/api/.env.example`

Required:

```env
APP_ENV=development
SERVICE_NAME=api-service
PORT=8000
DATABASE_URL=sqlite:///./upsk_sdf.db
JWT_SECRET=dev-secret
CORS_ORIGIN=http://localhost:3000
```

Optional:

```env
REDIS_URL=
MONGODB_URI=
API_KEY_A=
API_KEY_B=
CREATE_LINK_PER_MIN=30
LINKS_READ_PER_MIN=60
REDIRECT_PER_MIN=120
ANALYTICS_RETENTION_DAYS=30
DB_CONNECT_TIMEOUT_SECONDS=3
DB_POOL_TIMEOUT_SECONDS=3
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=5
DB_CIRCUIT_FAIL_MAX=3
DB_CIRCUIT_RESET_TIMEOUT_SECONDS=30
REDIS_SOCKET_TIMEOUT_SECONDS=3
```

Operational behavior:

- Changing `APP_ENV`, `PORT`, `DATABASE_URL`, `JWT_SECRET`, `SERVICE_NAME`, `API_KEY_A`, or `API_KEY_B` requires a service restart.
- Changing `DB_CONNECT_TIMEOUT_SECONDS`, `DB_POOL_TIMEOUT_SECONDS`, `DB_POOL_SIZE`, `DB_MAX_OVERFLOW`, `DB_CIRCUIT_FAIL_MAX`, `DB_CIRCUIT_RESET_TIMEOUT_SECONDS`, or `REDIS_SOCKET_TIMEOUT_SECONDS` requires a service restart because the app reads them at startup.
- Rate-limit variables and analytics retention settings should be treated as restart-required in the current implementation.
- `/ready` currently returns only `{"ready": true}` and does not validate downstream dependencies. Use a DB-backed route plus logs for real dependency diagnosis.

## Deploy

From the repo root:

```bash
docker build -t api-service:latest -f apps/api/Dockerfile .
docker run --name api-service --env-file apps/api/.env -p 8000:8000 api-service:latest
```

Verify:

```bash
curl -i http://localhost:8000/health
curl -i http://localhost:8000/ready
curl -s http://localhost:8000/metrics | grep http_requests_total
```

## Rollback

Stop the current container:

```bash
docker stop api-service
docker rm api-service
```

Run the previous known-good image:

```bash
docker run --name api-service --env-file apps/api/.env -p 8000:8000 api-service:previous-good
```

Verify rollback:

```bash
curl -i http://localhost:8000/health
curl -i http://localhost:8000/ready
```

## Ownership

Primary owner: API/backend owner
Slack channel: #api-oncall
Primary on-call: API/backend owner
Secondary on-call: platform/on-call engineer
Engineering manager: engineering-manager
If there is no response in 10 minutes, escalate from #api-oncall to the platform/on-call engineer by phone or PagerDuty.
Incident priority: page immediately for sustained 5xx errors, dependency outage, or severe latency increase
