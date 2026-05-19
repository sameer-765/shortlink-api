## Module 04 Build Recovery

### Why Recovery Was Needed

- Module 04 `BUILD` expected real Team Collaboration code to review.
- The workspace only contained the original URL-shortener app plus planning artifacts, so there was no honest review target for the five failure categories.

### Recovery Implemented

- Added `Team` and `TeamMember` models to `app/models.py`.
- Added `TeamCreate`, `TeamMemberCreate`, `TeamResponse`, and `TeamMemberResponse` schemas in `app/schemas/team.py`.
- Added `TeamsService` in `app/services/teams_service.py`.
- Added `POST /teams` and `POST /teams/{team_id}/members` in `app/routers/teams.py`.
- Registered the new teams router in `app/main.py`.
- Extended shared error-code mapping in `app/main.py` to include `403 -> forbidden` and `409 -> conflict`.
- Added request-level coverage in `tests/test_team_flow.py`.

### Workspace-Accurate Design Choices

- Used integer primary keys because the existing app already uses integer IDs.
- Used `principal_id` strings rather than a users-table foreign key because auth in this repo resolves to principals and no users table exists.
- Fit the new feature into the existing app-managed SQLAlchemy schema flow instead of inventing a migration system.

### Verification

- Focused suite: `.\\.venv\\Scripts\\python.exe -m pytest tests\\test_team_flow.py`
  - Result: `6 passed`
- Full suite: `.\\.venv\\Scripts\\python.exe -m pytest tests`
  - Result: `13 passed`

### Review Target Files For Module 04

- `app/models.py`
- `app/schemas/team.py`
- `app/services/teams_service.py`
- `app/routers/teams.py`
- `tests/test_team_flow.py`
