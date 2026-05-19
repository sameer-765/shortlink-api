from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class TeamActivityEvent(BaseModel):
    event_id: str
    event_type: str
    team_id: int
    actor_id: str
    target_type: str
    target_id: str
    created_at: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(extra="forbid")
