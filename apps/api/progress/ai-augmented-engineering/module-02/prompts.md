## Prompt 1: Create teams table and model

Implement a `teams` table or model in the existing database layer.

Context:
Use the current ORM and migration setup already present in the repo. Follow the same conventions used by existing models for naming, timestamps, primary keys, and relationships.

Requirements:
- Fields:
  - `id` (UUID primary key)
  - `name` (string, required)
  - `owner_id` (UUID foreign key to `users.id`)
  - `created_at`
  - `updated_at`
- Add proper constraints:
  - non-null `name`
  - valid foreign key for `owner_id`
  - explicit delete behavior for the owner relationship
- Generate and run a migration to create the table

Expected output:
- Model or schema definition for `teams`
- Migration file that creates the table

Acceptance criteria:
- Migration runs without errors
- Inserting a test team record via script or DB client succeeds
- Querying the table returns the inserted record with correct fields

Do not implement any API endpoints yet; focus only on persistence and schema.

## Prompt 2: Create `team_members` table and model

Implement the `team_members` table or model for team membership persistence.

Context:
Use the existing database or ORM setup and follow the same conventions as other models and migrations in the repo. This task depends on the `teams` table already existing with `id` as UUID and on an existing `users` table with `id` as UUID.

Requirements:
- Create a `team_members` table or model
- Fields:
  - `id` (UUID primary key)
  - `team_id` (UUID, required, foreign key to `teams.id`, `ON DELETE CASCADE`)
  - `user_id` (UUID, required, foreign key to `users.id`, `ON DELETE CASCADE`)
  - `role` (enum: `owner`, `admin`, `member`, required)
  - `created_at`
  - `updated_at`
- Add constraints:
  - unique constraint on `team_id` + `user_id`
  - non-null constraints on all required fields
- Do not insert any default records; this task is schema-only

Expected output:
- Model or schema definition for `team_members`
- Migration file that creates the table with the exact fields, enum, and constraints

Acceptance criteria:
- Migration runs successfully and creates the table
- Table has exact fields and types as specified
- Inserting a valid membership record via script succeeds
- Inserting a duplicate `team_id` + `user_id` pair fails due to the unique constraint
- Inserting invalid foreign keys fails due to FK constraints

Do not implement any API endpoints or business logic in this task; focus only on schema and persistence.

## Prompt 3: Add member endpoint

Implement an endpoint to add a user to a team: `POST /teams/{id}/members`.

Context:
Use the existing API framework, routing style, and database or ORM setup already present in the repo. Reuse the existing `team_members` table or model and follow patterns from similar protected endpoints for validation, error handling, and response format. Authentication is handled via `X-API-Key`, and the request should resolve the authenticated user through the shared auth dependency.

Requirements:
- Endpoint: `POST /teams/{id}/members`
- Headers: must include valid `X-API-Key`
- Body: `{ "user_id": string, "role": string }`
- Validate that the team exists
- Validate that the requester is authorized to add members
- Prevent duplicate memberships (`same user_id + team_id`)
- Insert a new record into `team_members` with `team_id`, `user_id`, and `role`
- Return a consistent JSON response

Auth rules:
- Missing or invalid API key -> return `401 Unauthorized`
- Authenticated but not allowed to add members -> return `403 Forbidden`
- The endpoint must not create the `owner` role

Expected output:
- Route handler implementation
- Validation logic
- DB insertion logic using existing models
- Request or response schema definitions if the codebase uses them

Acceptance criteria:
- Valid request with correct API key creates a membership record in DB
- Duplicate add attempt is rejected with a clear error
- Non-existent team returns `404 Not Found`
- Missing or invalid API key returns `401 Unauthorized`
- Unauthorized user returns `403 Forbidden`
- Response format matches existing API conventions

Do not implement invitation flow or email logic; only direct member addition via this endpoint.
