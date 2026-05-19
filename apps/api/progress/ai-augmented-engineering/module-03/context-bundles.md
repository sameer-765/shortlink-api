## Module 03 Context Bundles

### Task 1: Create teams table and model

#### Files to read

1. `app/models.py`
   Why: shows the shared SQLAlchemy model style, integer primary keys, timestamp defaults, and index patterns.
   If omitted: the agent may invent separate model modules or incompatible field conventions.

2. `app/database.py`
   Why: shows how schema creation and compatibility updates happen in this repo.
   If omitted: the model may be added without fitting the app-managed schema setup.

3. `app/dependencies/auth.py`
   Why: shows that identity is principal-based (`principal_a`, `principal_b`) rather than a users table.
   If omitted: the agent may design foreign keys against tables that do not exist.

4. `app/services/links_service.py`
   Why: shows the current persistence and commit pattern used by services.
   If omitted: the agent may use a mismatched write flow.

#### Files to modify

- `app/models.py`
- `app/database.py` only if a compatibility update is required for an existing table

#### Expected output format

- One `Team` SQLAlchemy model added to `app/models.py`
- Matching indexes or constraints in the same model file
- No endpoint or business-logic changes outside schema setup

### Task 2: Create `team_members` table and model

#### Files to read

1. `app/models.py`
   Why: ensures `team_id` matches the exact primary-key type and foreign-key style used in this repo.
   If omitted: the agent may create incompatible keys or index patterns.

2. `app/database.py`
   Why: shows how new tables become part of the initialized schema.
   If omitted: the schema may not be wired into the app's startup flow correctly.

3. `app/dependencies/auth.py`
   Why: shows that memberships should be principal-based, not tied to a missing users table.
   If omitted: the agent may guess the wrong identity model.

4. `tests/test_link_flow.py`
   Why: shows the repo's preference for proving behavior through request-level tests.
   If omitted: the agent may skip the right verification layer.

#### Files to modify

- `app/models.py`
- `app/database.py` only if a compatibility update is required for an existing table

#### Expected output format

- One `TeamMember` SQLAlchemy model in `app/models.py`
- A uniqueness rule on `team_id` plus `principal_id`
- No endpoint, auth, or invitation logic included

### Task 3: Implement `POST /teams/{id}/members`

#### Files to read

1. `app/routers/links.py`
   Why: shows protected-route dependency wiring, response-model usage, and error handling style.
   If omitted: endpoint implementation may drift from the app's router conventions.

2. `app/dependencies/auth.py`
   Why: shows the correct `X-API-Key` auth dependency and principal-scoping pattern.
   If omitted: the agent may invent custom auth logic.

3. `app/models.py`
   Why: shows the exact `Team` and `TeamMember` contract that the endpoint must use.
   If omitted: the agent may perform invalid queries or inserts.

4. `app/services/links_service.py`
   Why: shows where database writes belong and how service methods are structured.
   If omitted: the agent may place business logic directly in the router.

5. `tests/test_link_flow.py`
   Why: shows the API's error-envelope expectations and request-level test shape.
   If omitted: API behavior may be inconsistent.

#### Files to modify

- `app/routers/teams.py`
- `app/services/teams_service.py`
- `app/schemas/team.py`
- `tests/test_team_flow.py`

#### Expected output format

- New `POST /teams/{id}/members` route using shared `X-API-Key` auth
- Service logic for team-member creation and validation
- Request and response schema definitions
- Tests covering success, `401`, `403`, duplicate member, and `404` cases

## System-Level vs Task-Specific Split

- System-level:
  - project structure
  - FastAPI routing pattern
  - shared SQLAlchemy model style
  - principal-scoped auth via `X-API-Key`
  - response and error format rules
  - app-managed schema-init conventions
  - async or background processing rules

- Task-specific:
  - exact models, routers, services, schemas, and tests directly related to the current task being implemented

## Highest-Risk Omission

- Auth via `X-API-Key` is the most dangerous item to leave out of system-level context, because the agent may invent JWT or custom auth and create endpoints that look correct but do not match the app's real security model.
