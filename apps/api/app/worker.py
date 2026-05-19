from datetime import datetime
from typing import Optional

from app import database
from app.config import get_settings
from app.logging_utils import get_logger
from app.services.analytics_service import AnalyticsService

logger = get_logger()

try:
    from celery import Celery
except ImportError:  # pragma: no cover - dependency may not be installed locally yet
    Celery = None


def _broker_url() -> Optional[str]:
    return get_settings().redis_url or None


def _build_celery_app():
    if Celery is None:
        return None

    broker_url = _broker_url()
    if not broker_url:
        return None

    app = Celery("app.worker", broker=broker_url, backend=broker_url)
    app.conf.task_default_queue = "click-events"
    app.conf.task_acks_late = True
    return app


celery_app = _build_celery_app()


def enqueue_click_event(**payload) -> bool:
    if celery_app is None:
        return False

    celery_app.send_task("app.worker.process_click_event", kwargs=payload)
    return True


def _process_click_event(
    *,
    event_id: Optional[str],
    link_id: int,
    clicked_at: str,
    user_agent: Optional[str],
    referrer: Optional[str],
    ip_hash: Optional[str],
) -> bool:
    database.init_db()
    if database._SessionLocal is None:
        raise RuntimeError("Database session factory is not initialized")

    db = database._SessionLocal()
    try:
        service = AnalyticsService(db)
        inserted = service.record_click_event(
            event_id=event_id,
            link_id=link_id,
            clicked_at=datetime.fromisoformat(clicked_at),
            user_agent=user_agent,
            referrer=referrer,
            ip_hash=ip_hash,
        )
        logger.info(
            "click_event_processed event_id=%s link_id=%s inserted=%s",
            event_id,
            link_id,
            inserted,
        )
        return inserted
    finally:
        db.close()


if celery_app is not None:
    @celery_app.task(
        name="app.worker.process_click_event",
        autoretry_for=(Exception,),
        retry_kwargs={"max_retries": 3},
        retry_backoff=True,
    )
    def process_click_event(
        *,
        event_id: Optional[str],
        link_id: int,
        clicked_at: str,
        user_agent: Optional[str],
        referrer: Optional[str],
        ip_hash: Optional[str],
    ) -> bool:
        return _process_click_event(
            event_id=event_id,
            link_id=link_id,
            clicked_at=clicked_at,
            user_agent=user_agent,
            referrer=referrer,
            ip_hash=ip_hash,
        )

    @celery_app.task(name="app.worker.purge_old_clicks")
    def purge_old_clicks(retention_days: Optional[int] = None) -> int:
        database.init_db()
        if database._SessionLocal is None:
            raise RuntimeError("Database session factory is not initialized")

        db = database._SessionLocal()
        try:
            service = AnalyticsService(db)
            effective_retention = retention_days
            if effective_retention is None:
                effective_retention = get_settings().analytics_retention_days
            deleted = service.purge_old_clicks(effective_retention)
            logger.info(
                "analytics_retention_purged retention_days=%s deleted=%s",
                effective_retention,
                deleted,
            )
            return deleted
        finally:
            db.close()


def run_click_event_once(**payload) -> bool:
    return _process_click_event(**payload)


def run_purge_once(retention_days: Optional[int] = None) -> int:
    database.init_db()
    if database._SessionLocal is None:
        raise RuntimeError("Database session factory is not initialized")

    db = database._SessionLocal()
    try:
        service = AnalyticsService(db)
        effective_retention = retention_days
        if effective_retention is None:
            effective_retention = get_settings().analytics_retention_days
        return service.purge_old_clicks(effective_retention)
    finally:
        db.close()
