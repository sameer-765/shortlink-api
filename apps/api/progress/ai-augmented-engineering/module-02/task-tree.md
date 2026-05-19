## Module 02 Task Tree

### Task 1: Create teams table and model

- Input context needed:
  - Existing database setup
  - ORM or DB configuration
  - Current user model
  - Migration system
- Expected output:
  - `teams` table or model with ownership fields and timestamps
- Acceptance criteria:
  - Migration runs successfully
  - A team record can be inserted and queried with the expected values
  - `owner_id` matches the real user identifier type and relationship target
- Dependencies:
  - None

### Task 2: Create `team_members` table and model

- Input context needed:
  - `teams` schema from Task 1
  - Current user model
  - Existing relationship-table patterns
  - Migration system
- Expected output:
  - `team_members` table or model with membership role and uniqueness constraints
- Acceptance criteria:
  - Migration runs successfully
  - Valid membership records can be inserted
  - Duplicate `team_id` + `user_id` pairs are rejected
  - Role values are restricted to `owner`, `admin`, and `member`
- Dependencies:
  - Task 1

### Task 3: Implement `POST /teams/{id}/members`

- Input context needed:
  - Authentication mechanism using `X-API-Key`
  - User identity resolution from the request
  - `teams` schema from Task 1
  - `team_members` schema from Task 2
  - Existing protected endpoint and service patterns
- Expected output:
  - Protected endpoint `POST /teams/{id}/members`
  - Service logic for membership creation and authorization checks
  - Request and response schema definitions
  - Tests for success and failure cases
- Acceptance criteria:
  - Authenticated and authorized requests create a valid membership record
  - Missing or invalid API keys return `401 Unauthorized`
  - Unauthorized users return `403 Forbidden`
  - Unknown teams return `404 Not Found`
  - Duplicate membership attempts are rejected cleanly
- Dependencies:
  - Task 1
  - Task 2

## Critical Path

- Task 1 -> Task 2 -> Task 3

## Interface Contracts

### Contract: Task 1 -> Task 2

- Task 1 produces:
  - `teams` table with `id` (UUID primary key), `name` (non-null string), `owner_id` (UUID foreign key to `users.id` with defined delete behavior), `created_at`, and `updated_at`
- Task 2 expects:
  - The exact `teams` schema to exist and be queryable using stable field names and UUID identifier types

### Contract: Task 2 -> Task 3

- Task 2 produces:
  - `team_members` table with `id` (UUID primary key), `team_id` (UUID foreign key to `teams.id`), `user_id` (UUID foreign key to `users.id`), `role` (`owner` | `admin` | `member`), timestamps, and a unique constraint on `team_id` + `user_id`
- Task 3 expects:
  - The exact `team_members` schema to exist and be writable for validation, uniqueness enforcement, and membership creation
  - The endpoint must not create the `owner` role; ownership comes from earlier team-creation flow only

## Riskiest Task

- Task 3 is riskiest because it combines API logic, authorization, validation, and data consistency.
- Risk reduction:
  - Define an explicit authorization rule before implementation
  - Point the agent at the exact auth or middleware code that should enforce that rule
  - Keep schema decisions upstream so the endpoint only consumes an existing contract
