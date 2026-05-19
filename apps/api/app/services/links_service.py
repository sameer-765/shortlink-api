import random
import string
from datetime import datetime
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import Link


def generate_code(length: int = 6) -> str:
    """Generate a random short code."""
    chars = string.ascii_letters + string.digits
    return "".join(random.choices(chars, k=length))


def generate_unique_code(db: Session, length: int = 6) -> str:
    """Generate a unique short code that doesn't exist in the database."""
    while True:
        code = generate_code(length)
        existing = db.query(Link).filter(Link.code == code).first()
        if not existing:
            return code


class LinksService:
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def build_search_text(
        *,
        code: str,
        title: Optional[str],
        long_url: str,
        tags: Optional[str],
    ) -> str:
        parts = [code, title or "", long_url, tags or ""]
        return " ".join(part.strip() for part in parts if part and part.strip())

    def create_link(
        self,
        long_url: str,
        principal_id: str,
        title: Optional[str] = None,
        expires_at: Optional[datetime] = None,
        tags: Optional[str] = None,
    ) -> Link:
        """Create a new short link."""
        code = generate_unique_code(self.db)
        
        link = Link(
            code=code,
            title=title,
            long_url=long_url,
            search_text=self.build_search_text(
                code=code,
                title=title,
                long_url=long_url,
                tags=tags,
            ),
            created_by=principal_id,
            expires_at=expires_at,
            tags=tags,
        )
        
        self.db.add(link)
        self.db.commit()
        self.db.refresh(link)
        
        return link

    def get_link(self, link_id: int, principal_id: str) -> Optional[Link]:
        """Get a link by ID for the owning principal."""
        return (
            self.db.query(Link)
            .filter(Link.id == link_id, Link.created_by == principal_id)
            .first()
        )

    def get_link_by_code(self, code: str) -> Optional[Link]:
        """Get a link by its short code."""
        return self.db.query(Link).filter(Link.code == code).first()

    def list_links(
        self,
        principal_id: str,
        page: int = 1,
        page_size: int = 10,
    ) -> tuple[list[Link], int]:
        """List links owned by the current principal."""
        query = (
            self.db.query(Link)
            .filter(Link.created_by == principal_id)
            .order_by(Link.created_at.desc())
        )
        
        total = query.count()
        links = query.offset((page - 1) * page_size).limit(page_size).all()
        
        return links, total

    def search_links(
        self,
        *,
        principal_id: str,
        query: str,
        page: int = 1,
        page_size: int = 10,
    ) -> tuple[list[Link], int]:
        normalized_query = query.strip().lower()
        pattern = f"%{normalized_query}%"

        search_query = (
            self.db.query(Link)
            .filter(
                Link.created_by == principal_id,
                func.lower(func.coalesce(Link.search_text, "")).like(pattern),
            )
            .order_by(Link.created_at.desc())
        )

        total = search_query.count()
        links = search_query.offset((page - 1) * page_size).limit(page_size).all()
        return links, total

    def delete_link(self, link_id: int, principal_id: str) -> bool:
        """Delete a link by ID for the owning principal."""
        link = self.get_link(link_id, principal_id)
        if link:
            self.db.delete(link)
            self.db.commit()
            return True
        return False
