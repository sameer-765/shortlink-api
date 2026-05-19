from datetime import datetime
from typing import Literal

from pydantic import BaseModel, field_validator


class TeamCreate(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("name cannot be empty or whitespace only")
        return normalized


class TeamResponse(BaseModel):
    id: int
    name: str
    owner_principal_id: str
    created_at: datetime

    model_config = {"from_attributes": True}


class TeamMemberCreate(BaseModel):
    principal_id: str
    role: Literal["admin", "member"]

    @field_validator("principal_id")
    @classmethod
    def validate_principal_id(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("principal_id cannot be empty or whitespace only")
        return normalized


class TeamMemberResponse(BaseModel):
    id: int
    team_id: int
    principal_id: str
    role: str
    created_at: datetime

    model_config = {"from_attributes": True}
