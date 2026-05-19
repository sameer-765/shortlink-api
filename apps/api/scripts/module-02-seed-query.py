"""Module 02 seed query script - proves the core query shape works."""
import os
import sys
from pathlib import Path

# Add the api directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load .env file
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

from sqlalchemy import select

from app.database import init_db, _SessionLocal
from app.models import Link


def main():
    init_db()
    from app.database import _SessionLocal
    db = _SessionLocal()
    
    try:
        # Insert a test link
        link = Link(code="test123", long_url="https://example.com", created_by="test_user")
        db.add(link)
        db.commit()
        db.refresh(link)
        
        print(f"Inserted code: {link.code}")
        
        # Query by code (the hot path)
        result = db.execute(select(Link).where(Link.code == "test123"))
        found_link = result.scalar_one()
        
        print(f"Selected code: {found_link.code}")
        print(f"Matched long_url: {found_link.long_url}")
        
    finally:
        db.close()


if __name__ == "__main__":
    main()