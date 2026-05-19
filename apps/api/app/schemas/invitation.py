from datetime import datetime
from typing import Literal

from pydantic import BaseModel, field_validator


class InvitationCreate(BaseModel):
    email: str
    role: Literal["admin", "member"]

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        normalized = value.strip().lower()
        if not normalized:
            raise ValueError("email cannot be empty or whitespace only")
        if "@" not in normalized:
            raise ValueError("email must be a valid email address")
        return normalized


class InvitationResponse(BaseModel):
    id: int
    team_id: int
    email: str
    role: str
    invited_by: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
