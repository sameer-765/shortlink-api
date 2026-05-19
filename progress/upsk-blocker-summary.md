# UPSK Blocker Summary

Date checked: 2026-05-05

## Local repo status

- `progress/state.json` shows all System Design modules marked `complete`.
- Local API verification passed with:

```powershell
$env:PYTHONPATH='D:\CAW sp\apps\api'
$env:PORT='8000'
$env:API_KEY_A='testkey'
$env:DATABASE_URL='sqlite:///./upsk_sdf.db'
.\.venv\Scripts\python.exe -m unittest discover -s apps\api\tests -v
```

- Result: 7 tests passed across:
  - `apps/api/tests/test_link_flow.py`
  - `apps/api/tests/test_search_flow.py`
  - `apps/api/tests/test_analytics_flow.py`

## UPSK CLI state

- CLI upgraded successfully to `upsk 0.1.22`.
- `upsk login` succeeded.
- `upsk start --skill system-design-fundamentals --json` reports the skill is already complete.
- `upsk start --skill ai-augmented-engineering --json` returns `workspace_required`.
- `upsk start --skill debugging-incident-response --json` returns the same `workspace_required`.

## Exact blocker

UPSK says:

- System Design Fundamentals is complete
- but the app foundation evidence is missing
- and downstream skills cannot start until that evidence is recognized

This appears to be a platform/session-state inconsistency, not a failing local implementation.

## Additional inconsistency observed

`upsk catalog --json` shows:

- `system-design-fundamentals` has `completed_sessions: 1`
- but the catalog summary also reports `total_modules_completed: 0`

## Filed report

- UPSK feedback report ID: `fb_DOXWPSfQ8tdckyt_`
- GitHub issue: `#652`

## Latest retry

- On 2026-05-05, `upsk start --skill system-design-fundamentals --json` was retried after login and CLI upgrade.
- Result was unchanged: the skill is reported as already complete, retakes are unavailable, and no active session is created.
- This confirms there is still no CLI path to reopen System Design and no way to satisfy the downstream workspace gate from the local side.

## Useful commands

```powershell
.\upsk.exe status --json
.\upsk.exe status --all --json
.\upsk.exe start --skill system-design-fundamentals --json
.\upsk.exe start --skill ai-augmented-engineering --json
.\upsk.exe start --skill debugging-incident-response --json
.\upsk.exe catalog --json
```
