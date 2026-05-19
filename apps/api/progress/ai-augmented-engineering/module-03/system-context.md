## Module 03 System-Level Context

### Architecture Summary

- FastAPI backend in `apps/api` with a modular structure under `app/`.
- Routers, schemas, services, and tests are separated into dedicated folders.
- SQLAlchemy with SQLite by default, with environment-based config overrides.
- Persistence models live in the shared `app/models.py` module rather than one file per model.
- Schema creation is app-managed in `app/database.py` via `Base.metadata.create_all(...)` and targeted compatibility updates, not a standalone migration tool.
- Routes are grouped in router modules and registered in the main app entrypoint.
- Auth uses a shared `X-API-Key` dependency and common middleware patterns.
- Auth resolves callers to scoped principals such as `principal_a` and `principal_b`; there is no separate users table in this workspace.
- Existing async or background utilities should be reused, not duplicated.

### Coding Conventions

- Follow the existing folder structure: routers in `app/routers/`, schemas in `app/schemas/`, services in `app/services/`, and tests in `tests/`.
- Use consistent naming conventions: snake_case for files and functions, PascalCase for schema or model classes.
- Keep business logic inside services, not directly inside route handlers.
- Use shared validation patterns through existing schema models instead of manual request parsing.
- Return consistent JSON error responses with proper HTTP status codes such as `401`, `403`, and `404`.
- Protected routes must use the shared `X-API-Key` auth dependency, not custom per-route auth logic.
- Database changes must fit the existing `app/models.py` plus `app/database.py` schema-init pattern and be verified with tests against the live SQLite setup.

### Constraints

- Must use shared `X-API-Key` auth for protected routes.
- Must follow existing project structure and patterns.
- Must apply DB changes through the existing SQLAlchemy model and schema-init flow.
- Must not add undefined fields, roles, or behaviors.
- Must reuse existing async or background utilities.
- Must return consistent JSON responses and HTTP status codes.
