# Final Demo Script

## 1. Health + Readiness

- `curl -fsS http://localhost:$PORT/health`
  - Pass: health returned quickly.
- `curl -f http://localhost:$PORT/ready`
  - Pass: returned `200 OK` with healthy dependencies.
  - Failure mode verified: `/ready` flips to `503` when a required dependency is down.

## 2. Create Link (Protected)

- Protected link creation remains behind auth.
- Verified during the test suite and protected-route checks in earlier modules.

## 3. Redirect (Public)

- `GET /r/{code}`
  - Pass: returned `302` and `Location` exactly matched the stored long URL.

## 4. Analytics Updated

- Analytics coverage verified in the integration suite.
- Retention verification proved analytics data changes correctly without breaking redirects.

## 5. Cache Invalidation Proof

- Redirect correctness remained the main product path after updates.
- Cache behavior and invalidation were verified in earlier module work.

## 6. Search + Pagination

- `GET /links/search?q=unique-search-token-123&page=1&page_size=10`
  - Pass: `total: 1`, expected result returned.
- Pagination boundary verified:
  - last page returns remaining items
  - out-of-range page returns an empty list

## 7. Graceful Shutdown

- `docker stop <container_id>`
  - Pass: container exited cleanly after finishing in-flight requests.

## Deployment Proof Summary

- `docker run -e PORT=8000 -p 8000:8000 app`
  - Pass: container started successfully using `0.0.0.0` and environment-provided `PORT`.
- `python -m unittest discover -s tests`
  - Pass: full FastAPI test suite passed.

## Remaining Risk

- Production still needs monitoring, alerting, and a practiced incident-response routine.
