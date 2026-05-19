from datetime import datetime
from typing import Optional

from pydantic import BaseModel, UrlConstraints, field_validator
from pydantic.types import constr


class LinkBase(BaseModel):
    title: Optional[str] = None
    long_url: str
    expires_at: Optional[datetime] = None
    tags: Optional[str] = None


class LinkCreate(LinkBase):
    @field_validator("long_url")
    @classmethod
    def validate_long_url(cls, v: str) -> str:
        # Strip whitespace and check for control characters
        stripped = v.strip()
        if not stripped:
            raise ValueError("long_url cannot be empty or whitespace only")
        
        # Check for control characters (except tab, newline, carriage return which we already stripped)
        for char in stripped:
            if ord(char) < 32 and char not in '\t\n\r':
                raise ValueError("long_url contains invalid control characters")
        
        # Check for dangerous schemes (case-insensitive)
        lower_url = stripped.lower()
        dangerous_schemes = [
            "javascript:", "vbscript:", "data:", "file:", 
            "ftp:", "mailto:", "tel:", "ssh:"
        ]
        for scheme in dangerous_schemes:
            if lower_url.startswith(scheme):
                raise ValueError(f"URL scheme '{scheme}' is not allowed")
        
        # Check for scheme-relative URLs
        if stripped.startswith("//"):
            raise ValueError("Scheme-relative URLs are not allowed")
        
        # Check for encoded attacks
        if "%2f" in lower_url or "%2f" in lower_url.replace("%2f", ""):
            # Allow normal %2F in query strings, but reject obvious bypass attempts
            if "http:%2f" in lower_url or "http%3a%2f" in lower_url:
                raise ValueError("Encoded slashes in scheme are not allowed")
        
        # Check for backslash variants
        if "\\\\" in stripped or "\\" in stripped.split("://", 1)[-1]:
            raise ValueError("Backslashes are not allowed in URLs")
        
        # Must start with http or https
        if not (stripped.startswith("http://") or stripped.startswith("https://")):
            raise ValueError("URL must start with http:// or https://")
        
        return stripped


class LinkResponse(BaseModel):
    id: int
    code: str
    short_url: str
    title: Optional[str] = None
    long_url: str
    created_at: datetime
    created_by: Optional[str] = None
    expires_at: Optional[datetime] = None
    tags: Optional[str] = None

    model_config = {"from_attributes": True}


class LinkListResponse(BaseModel):
    links: list[LinkResponse]
    total: int
    page: int
    page_size: int


class LinkAnalyticsResponse(BaseModel):
    link_id: int
    click_count: int
    last_clicked_at: Optional[datetime] = None
