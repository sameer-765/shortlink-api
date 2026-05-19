import json
from datetime import datetime
from uuid import uuid4

from sqlalchemy.orm import Session

from app.models import AuditLog
from app.schemas.activity import TeamActivityEvent


class AuditService:
    def __init__(self, db: Session):
        self.db = db

    def record_event(
        self,
        *,
        event_type: str,
        team_id: int,
        actor_id: str,
        target_type: str,
        target_id: str,
        metadata: dict[str, object] | None = None,
    ) -> TeamActivityEvent:
        event = TeamActivityEvent(
            event_id=str(uuid4()),
            event_type=event_type,
            team_id=team_id,
            actor_id=actor_id,
            target_type=target_type,
            target_id=target_id,
            created_at=datetime.utcnow(),
            metadata=metadata or {},
        )

        audit_entry = AuditLog(
            event_id=event.event_id,
            event_type=event.event_type,
            team_id=event.team_id,
            actor_id=event.actor_id,
            target_type=event.target_type,
            target_id=event.target_id,
            metadata_json=json.dumps(event.metadata, sort_keys=True),
            created_at=event.created_at,
        )
        self.db.add(audit_entry)
        return event
