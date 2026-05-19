# Module 01 Diagnosis Notes

## Bug 1
- Symptom: The API never starts on port 3000 and `curl http://localhost:3000/health` fails with connection refused.
- Hypothesis A:
  - Command: `docker compose -f infra/docker-compose.yml ps`
  - Observation: `linkops-postgres` and `linkops-redis` were both healthy, so the dependency containers were not the thing crashing first.
- Hypothesis B:
  - Command: `docker logs linkops-api --tail 80` and `docker inspect linkops-api --format "{{range .Config.Env}}{{println .}}{{end}}"`
  - Observation: The traceback showed `Settings` missing `database_url`, and the container env had `DB_URL=sqlite:////data/linkops.db` but no `DATABASE_URL`.
- Fix: Renamed the runtime variable from `DB_URL` to `DATABASE_URL` for both the API and worker services in `infra/docker-compose.yml`.
- Verification proof: `docker compose -f infra/docker-compose.yml ps` showed `linkops-api` healthy on `0.0.0.0:3000`, `curl -i http://localhost:3000/health` returned `HTTP/1.1 200 OK` with `{"ok":true}`, `docker inspect linkops-api` showed `DATABASE_URL=sqlite:////data/linkops.db`, and `docker logs linkops-worker --tail 40` showed the worker connected to `redis://redis:6379/0` and ready.

## Bug 2
- Symptom: The module expected duplicate items across page boundaries, so I tested whether pagination overlap still exists in this workspace.
- Hypothesis A:
  - Command: Seed 25 links, then request `GET /links?page=1&page_size=10`, `GET /links?page=2&page_size=10`, and `GET /links?page=3&page_size=10` with `X-API-Key: linkops-local-key-a`.
  - Observation: Page 1 returned IDs `25..16`, page 2 returned `15..6`, and page 3 returned `5..1` with no overlap.
- Hypothesis B:
  - Command: Inspect `apps/api/app/services/links_service.py` for offset math and ordering.
  - Observation: The implementation already uses `offset((page - 1) * page_size).limit(page_size)` with descending `created_at` ordering, so the current workspace already contains the corrected pagination logic.
- Fix: No code fix was needed for Bug 2 in this workspace because the pagination issue was not reproducible.
- Verification proof: Raw API responses for pages 1-3 showed distinct, non-overlapping IDs and `total: 25`.
