import hashlib
from datetime import date, datetime, time, timedelta
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import ClickEvent, Link


class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def hash_ip(ip_address: Optional[str]) -> Optional[str]:
        if not ip_address:
            return None
        return hashlib.sha256(ip_address.encode("utf-8")).hexdigest()

    @staticmethod
    def window_start(day: date) -> datetime:
        return datetime.combine(day, time.min)

    @staticmethod
    def window_end(day: date) -> datetime:
        return datetime.combine(day, time.max)

    def record_click_event(
        self,
        *,
        event_id: Optional[str],
        link_id: int,
        clicked_at: datetime,
        user_agent: Optional[str],
        referrer: Optional[str],
        ip_hash: Optional[str],
    ) -> bool:
        if event_id:
            existing = (
                self.db.query(ClickEvent)
                .filter(ClickEvent.event_id == event_id)
                .first()
            )
            if existing:
                return False

        event = ClickEvent(
            event_id=event_id,
            link_id=link_id,
            clicked_at=clicked_at,
            user_agent=user_agent,
            referrer=referrer,
            ip_hash=ip_hash,
        )
        self.db.add(event)
        self.db.commit()
        return True

    def get_link_analytics(
        self,
        *,
        link_id: int,
        principal_id: str,
        from_dt: datetime,
        to_dt: datetime,
    ) -> Optional[dict[str, object]]:
        link = (
            self.db.query(Link)
            .filter(Link.id == link_id, Link.created_by == principal_id)
            .first()
        )
        if not link:
            return None

        count, last_clicked_at = (
            self.db.query(
                func.count(ClickEvent.id),
                func.max(ClickEvent.clicked_at),
            )
            .filter(
                ClickEvent.link_id == link_id,
                ClickEvent.clicked_at >= from_dt,
                ClickEvent.clicked_at <= to_dt,
            )
            .one()
        )

        return {
            "link_id": link_id,
            "click_count": int(count or 0),
            "last_clicked_at": last_clicked_at,
        }

    def purge_old_clicks(self, retention_days: int) -> int:
        cutoff = datetime.utcnow() - timedelta(days=retention_days)
        deleted = (
            self.db.query(ClickEvent)
            .filter(ClickEvent.clicked_at < cutoff)
            .delete(synchronize_session=False)
        )
        self.db.commit()
        return int(deleted or 0)
