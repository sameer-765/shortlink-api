# shortlink-api

A FastAPI-based URL shortener API with team collaboration features, authorization checks, audit events, health endpoints, and container-ready deployment.

## What This Repo Includes

- Short link creation and redirect flows
- Team management for shared link ownership
- Invitation flows for adding users to teams
- Commenting on team links
- Audit and activity event tracking
- Health and readiness endpoints for operations
- Prometheus metrics endpoint
- GitHub Actions coverage for auth regression tests and Docker smoke tests

## Tech Stack

- Python 3.12
- FastAPI
- SQLAlchemy
- Pydantic Settings
- Uvicorn
- SQLite for local development and CI smoke checks
- Docker

## Project Layout

```text
apps/api/
  app/          FastAPI app, routers, services, config, database code
  tests/        Unit and flow tests
  scripts/      CI helper scripts
  Dockerfile    Container image definition
```

## Main API Areas

- `POST /links` create a shortened link
- `GET /r/{code}` resolve and redirect a short link
- `POST /teams` create a team
- `POST /teams/{team_id}/members` add team members
- `POST /teams/{team_id}/invitations` create invitations
- `DELETE /teams/{team_id}/invitations/{invitation_id}` revoke invitations
- `POST /teams/{team_id}/links/{link_id}/comments` add comments
- `DELETE /teams/{team_id}/links/{link_id}/comments/{comment_id}` delete comments
- `GET /live` liveness probe
- `GET /ready` readiness probe
- `GET /metrics` Prometheus metrics

## Local Setup

1. Create a virtual environment.
2. Install dependencies from `apps/api/requirements.txt`.
3. Copy `apps/api/.env.example` to `apps/api/.env`.
4. Fill in required values for:
   - `APP_ENV`
   - `PORT`
   - `DATABASE_URL`
   - `JWT_SECRET`
   - `SERVICE_NAME`
   - `API_KEY_A`
   - `API_KEY_B`
5. Start the API from `apps/api`.

Example commands on Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r apps/api/requirements.txt
Copy-Item apps/api/.env.example apps/api/.env
Set-Location apps/api
..\..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## Running Tests

Run the focused auth regression suite:

```powershell
Set-Location apps/api
..\..\.venv\Scripts\python.exe -m unittest -v tests.test_invitations tests.test_comments tests.test_audit_events
```

Run the broader test suite:

```powershell
Set-Location apps/api
..\..\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

## Docker

Build the API image:

```powershell
docker build -t shortlink-api .\apps\api
```

Run it locally:

```powershell
docker run --rm -p 8000:8000 `
  -e APP_ENV=development `
  -e PORT=8000 `
  -e DATABASE_URL=sqlite:////data/local.db `
  -e JWT_SECRET=local-secret `
  -e SERVICE_NAME=api-service `
  -e API_KEY_A=local-key-a `
  -e API_KEY_B=local-key-b `
  shortlink-api
```

## CI

This repo uses GitHub Actions for two main checks:

- `CI`
  - installs Python dependencies
  - runs focused auth regression tests
  - builds the Docker image on `main`
  - runs a container smoke test
  - pushes the image to GHCR on successful `main` pushes

- `API Auth Gate`
  - runs the focused auth regression suite on a Windows runner
  - ensures authorization-sensitive flows stay protected

## Authorization Expectations

- Mutating endpoints must enforce authorization server-side
- Cross-team access must be denied
- Unauthorized requests must not change database state
- Unauthorized requests must not emit audit events
- New protected endpoints should ship with both success-path and denial-path tests

## Notes

- Local runtime settings are loaded through Pydantic Settings from `apps/api/.env`.
