from datetime import datetime

from pydantic import BaseModel, field_validator


class CommentCreate(BaseModel):
    body: str
    parent_id: int | None = None

    @field_validator("body")
    @classmethod
    def validate_body(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("body cannot be empty or whitespace only")
        return normalized


class CommentResponse(BaseModel):
    id: int
    team_id: int
    link_id: int
    author_id: str
    body: str
    parent_id: int | None
    created_at: datetime

    model_config = {"from_attributes": True}
