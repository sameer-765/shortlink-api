## Folder Structure

- `app/main.py`: FastAPI entrypoint, middleware, exception handlers, health endpoints, and router registration.
- `app/routers/`: HTTP route modules. Current routers are `links.py` and `redirect.py`.
- `app/services/`: Business logic. `links_service.py` handles link CRUD/search logic, and `analytics_service.py` handles click analytics and retention.
- `app/schemas/`: Pydantic request/response models and validation.
- `app/dependencies/`: Reusable request dependencies for authentication and rate limiting.
- `app/database.py`: SQLAlchemy engine/session setup plus lightweight schema-update logic.
- `app/models.py`: SQLAlchemy models.
- `app/worker.py`: Optional Celery background jobs for click-event processing and retention cleanup.
- `app/config.py`: Environment-variable settings loader.
- `app/logging_utils.py`: Shared logger setup.
- `tests/`: API behavior tests.

## Data Models

### Link

- Fields: `id`, `code`, `title`, `long_url`, `search_text`, `created_at`, `created_by`, `expires_at`, `tags`
- Ownership is modeled through `created_by`, which stores the authenticated principal identifier.

### ClickEvent

- Fields: `id`, `link_id`, `event_id`, `clicked_at`, `user_agent`, `referrer`, `ip_hash`
- `link_id` references `Link.id`

## Routes

- `GET /health`: public health check
- `GET /ready`: public readiness check
- `POST /links`: protected by `X-API-Key`; creates a short link
- `GET /links/search`: protected; owner-scoped search
- `GET /links`: protected; owner-scoped paginated listing
- `GET /links/{link_id}`: protected; owner-scoped fetch by ID
- `GET /links/{link_id}/analytics?from=&to=`: protected; owner-scoped analytics
- `GET /r/{code}`: public redirect endpoint with redirect-specific rate limiting

## Authentication And Middleware

- Authentication is API-key based, not user/session/JWT based in current route behavior.
- `require_principal_id` reads the `X-API-Key` header, compares it to configured keys, and maps callers to `principal_a` or `principal_b`.
- Missing or invalid API keys return `401`.
- Missing API-key configuration returns `503`.
- Global HTTP middleware adds a request ID, logs request completion/failure, and attaches `X-Request-ID` to responses.
- Global exception handlers normalize HTTP, validation, and unhandled errors into a common error envelope.
- Rate limiting is dependency-based and in-memory:
  - create-link limit per principal
  - links-read limit per principal
  - redirect limit per client host

## Database And Configuration

- SQLAlchemy is used directly; there is no dedicated migration tool like Alembic.
- `database.py` initializes the engine/session and calls `Base.metadata.create_all(...)`.
- `database.py` also performs manual schema patching with raw SQL for missing columns and indexes.
- Default database is SQLite via `sqlite:///./upsk_sdf.db` if `DATABASE_URL` is unset.
- Settings are loaded from `.env` using `pydantic-settings`.
- Config fields include `PORT`, `DATABASE_URL`, `MONGODB_URI`, `REDIS_URL`, `JWT_SECRET`, `API_KEY_A`, `API_KEY_B`, rate limits, and analytics retention settings.

## Security-Sensitive Areas

- `app/dependencies/auth.py`: protected access control entry point
- `app/dependencies/rate_limit.py`: abuse prevention/rate limits
- `app/schemas/link.py`: input validation, including URL scheme restrictions
- `app/routers/redirect.py`: public redirect behavior and analytics enqueue path
- `app/database.py`: database URL handling and schema mutation logic

## Shared Utilities

- `get_settings()` for config
- `get_logger()` for logging
- `get_db()` for DB session injection
- auth and rate-limit dependency helpers in `app/dependencies/`

## Background Jobs And Async Systems

- `app/worker.py` contains optional Celery integration
- Redis is used as the broker/backend if `REDIS_URL` is configured
- Redirect requests enqueue click-event processing asynchronously
- There is also a retention-cleanup task for old analytics events

## Extension Points

- New API routes: add a router module under `app/routers/` and include it in `app/main.py`
- New models: extend `app/models.py` or split model modules if the codebase grows
- New schemas: add request/response contracts under `app/schemas/`
- New business logic: add services under `app/services/`
- New protected behaviors: extend auth/authorization dependencies under `app/dependencies/`
- New async work: extend `app/worker.py` for background jobs

## Team Collaboration Integration Notes

- Team invites would likely need a new model, schema, router, and service using the existing dependency and service patterns.
- Audit logs could follow a model/service pattern similar to analytics, but for protected actions instead of redirects.
- Activity feeds could reuse the async worker pattern if event generation needs to happen out of band.
- Role-based permissions would require a new authorization layer beyond the current API-key identity mapping.
