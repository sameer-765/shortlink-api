from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import require_principal_id
from app.dependencies.rate_limit import (
    enforce_create_link_rate_limit,
    enforce_read_links_rate_limit,
)
from app.schemas.link import (
    LinkAnalyticsResponse,
    LinkCreate,
    LinkListResponse,
    LinkResponse,
)
from app.services.analytics_service import AnalyticsService
from app.services.links_service import LinksService

router = APIRouter(prefix="/links", tags=["links"])


def get_links_service(db: Session = Depends(get_db)) -> LinksService:
    return LinksService(db)


def get_analytics_service(db: Session = Depends(get_db)) -> AnalyticsService:
    return AnalyticsService(db)


@router.post("", response_model=LinkResponse, status_code=201)
def create_link(
    link_data: LinkCreate,
    service: LinksService = Depends(get_links_service),
    principal_id: str = Depends(require_principal_id),
    _: None = Depends(enforce_create_link_rate_limit),
) -> LinkResponse:
    """Create a new short link."""
    # Check if expires_at is in the future if provided
    if link_data.expires_at and link_data.expires_at <= datetime.utcnow():
        raise HTTPException(
            status_code=400,
            detail="expires_at must be in the future"
        )
    
    link = service.create_link(
        long_url=link_data.long_url,
        principal_id=principal_id,
        title=link_data.title,
        expires_at=link_data.expires_at,
        tags=link_data.tags,
    )
    
    # Build the short URL
    short_url = f"/r/{link.code}"
    
    return LinkResponse(
        id=link.id,
        code=link.code,
        short_url=short_url,
        title=link.title,
        long_url=link.long_url,
        created_at=link.created_at,
        created_by=link.created_by,
        expires_at=link.expires_at,
        tags=link.tags,
    )


@router.get("/search", response_model=LinkListResponse)
def search_links(
    q: str = Query(..., min_length=1, description="Search query"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    service: LinksService = Depends(get_links_service),
    principal_id: str = Depends(require_principal_id),
    _: None = Depends(enforce_read_links_rate_limit),
) -> LinkListResponse:
    """Search owner-scoped links using a parameterized query."""
    links, total = service.search_links(
        principal_id=principal_id,
        query=q,
        page=page,
        page_size=page_size,
    )

    return LinkListResponse(
        links=[
            LinkResponse(
                id=link.id,
                code=link.code,
                short_url=f"/r/{link.code}",
                title=link.title,
                long_url=link.long_url,
                created_at=link.created_at,
                created_by=link.created_by,
                expires_at=link.expires_at,
                tags=link.tags,
            )
            for link in links
        ],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("", response_model=LinkListResponse)
def list_links(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    service: LinksService = Depends(get_links_service),
    principal_id: str = Depends(require_principal_id),
    _: None = Depends(enforce_read_links_rate_limit),
) -> LinkListResponse:
    """List links owned by the authenticated principal."""
    links, total = service.list_links(
        principal_id=principal_id,
        page=page,
        page_size=page_size,
    )
    
    link_responses = [
        LinkResponse(
            id=link.id,
            code=link.code,
            short_url=f"/r/{link.code}",
            title=link.title,
            long_url=link.long_url,
            created_at=link.created_at,
            created_by=link.created_by,
            expires_at=link.expires_at,
            tags=link.tags,
        )
        for link in links
    ]
    
    return LinkListResponse(
        links=link_responses,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{link_id}", response_model=LinkResponse)
def get_link(
    link_id: int,
    service: LinksService = Depends(get_links_service),
    principal_id: str = Depends(require_principal_id),
    _: None = Depends(enforce_read_links_rate_limit),
) -> LinkResponse:
    """Get a link by ID for the authenticated principal."""
    link = service.get_link(link_id, principal_id)
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    
    return LinkResponse(
        id=link.id,
        code=link.code,
        short_url=f"/r/{link.code}",
        title=link.title,
        long_url=link.long_url,
        created_at=link.created_at,
        created_by=link.created_by,
        expires_at=link.expires_at,
        tags=link.tags,
    )


@router.get("/{link_id}/analytics", response_model=LinkAnalyticsResponse)
def get_link_analytics(
    link_id: int,
    from_date: date = Query(..., alias="from", description="Start date"),
    to_date: date = Query(..., alias="to", description="End date"),
    analytics_service: AnalyticsService = Depends(get_analytics_service),
    principal_id: str = Depends(require_principal_id),
    _: None = Depends(enforce_read_links_rate_limit),
) -> LinkAnalyticsResponse:
    """Get owner-scoped click analytics for one link over a time window."""
    analytics = analytics_service.get_link_analytics(
        link_id=link_id,
        principal_id=principal_id,
        from_dt=AnalyticsService.window_start(from_date),
        to_dt=AnalyticsService.window_end(to_date),
    )
    if not analytics:
        raise HTTPException(status_code=404, detail="Link not found")

    return LinkAnalyticsResponse(**analytics)
