from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.rate_limit import enforce_redirect_rate_limit
from app.logging_utils import get_logger
from app.services.analytics_service import AnalyticsService
from app.services.links_service import LinksService
from app.worker import enqueue_click_event

router = APIRouter(prefix="/r", tags=["redirect"])
logger = get_logger()


def get_links_service(db: Session = Depends(get_db)) -> LinksService:
    return LinksService(db)


@router.get("/{code}")
def redirect_to_long_url(
    code: str,
    request: Request,
    service: LinksService = Depends(get_links_service),
    _: None = Depends(enforce_redirect_rate_limit),
):
    """Redirect to the original long URL."""
    link = service.get_link_by_code(code)
    
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    
    if link.expires_at and link.expires_at <= datetime.utcnow():
        raise HTTPException(status_code=410, detail="Link has expired")

    client_ip = request.client.host if request.client else None
    payload = {
        "event_id": getattr(request.state, "request_id", None),
        "link_id": link.id,
        "clicked_at": datetime.utcnow().isoformat(),
        "user_agent": request.headers.get("user-agent"),
        "referrer": request.headers.get("referer"),
        "ip_hash": AnalyticsService.hash_ip(client_ip),
    }

    try:
        enqueued = enqueue_click_event(**payload)
        if enqueued:
            logger.info(
                "analytics_enqueued request_id=%s link_id=%s",
                payload["event_id"],
                link.id,
            )
        else:
            logger.warning(
                "analytics_enqueue_skipped request_id=%s link_id=%s",
                payload["event_id"],
                link.id,
            )
    except Exception:
        logger.exception(
            "analytics_enqueue_failed request_id=%s link_id=%s",
            payload["event_id"],
            link.id,
        )

    return RedirectResponse(url=link.long_url, status_code=302)
