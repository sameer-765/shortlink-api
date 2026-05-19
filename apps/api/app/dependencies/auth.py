import secrets

from fastapi import Header, HTTPException, Request, status

from app.config import get_settings


def require_principal_id(
    request: Request,
    x_api_key: str | None = Header(None, alias="X-API-Key"),
) -> str:
    """Validate the caller API key and return the scoped principal id."""
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-API-Key header",
        )

    settings = get_settings()
    configured_keys = {
        settings.api_key_a: "principal_a",
        settings.api_key_b: "principal_b",
    }

    for configured_key, principal_id in configured_keys.items():
        if configured_key and secrets.compare_digest(x_api_key, configured_key):
            request.state.principal_id = principal_id
            return principal_id

    if not any(configured_keys):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="API key auth is not configured",
        )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid API key",
    )
