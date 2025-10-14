"""
Database configuration for the AI Content Factory application
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Create database engine with proper encoding settings
# Use SQLite for testing when DATABASE_URL is not set
if settings.DATABASE_URL:
    engine = create_engine(
        settings.DATABASE_URL, 
        pool_pre_ping=True,
        pool_recycle=300,
        connect_args={
            "options": "-c timezone=utc",
            "client_encoding": "utf8"
        }
    )
else:
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})

# Create a SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a Base class
Base = declarative_base()


def get_db():
    """
    Dependency to get a database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()