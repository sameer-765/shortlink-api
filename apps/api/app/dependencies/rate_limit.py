from collections import defaultdict, deque
from time import time

from fastapi import Depends, HTTPException, Request, status

from app.config import get_settings
from app.dependencies.auth import require_principal_id

_WINDOW_SECONDS = 60
_request_windows: dict[str, deque[float]] = defaultdict(deque)


def _enforce_limit(bucket: str, limit: int) -> None:
    now = time()
    window = _request_windows[bucket]

    while window and now - window[0] >= _WINDOW_SECONDS:
        window.popleft()

    if len(window) >= limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded",
        )

    window.append(now)


def enforce_create_link_rate_limit(
    principal_id: str = Depends(require_principal_id),
) -> None:
    settings = get_settings()
    _enforce_limit(f"create-link:{principal_id}", settings.create_link_per_min)


def enforce_read_links_rate_limit(
    principal_id: str = Depends(require_principal_id),
) -> None:
    settings = get_settings()
    _enforce_limit(f"links-read:{principal_id}", settings.links_read_per_min)


def enforce_redirect_rate_limit(request: Request) -> None:
    settings = get_settings()
    client_host = request.client.host if request.client else "unknown"
    _enforce_limit(f"redirect:{client_host}", settings.redirect_per_min)
