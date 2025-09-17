"""
Dependencies for the AI Content Factory API
"""
from typing import Generator

from sqlalchemy.orm import Session

from app.core.database import get_db


def get_database() -> Generator[Session, None, None]:
    """
    FastAPI dependency to get a database session
    """
    db = next(get_db())
    try:
        yield db
    finally:
        db.close()