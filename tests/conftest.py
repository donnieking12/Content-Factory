"""
Pytest configuration for the AI Content Factory application
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base
from app.core.config import settings


@pytest.fixture(scope="session")
def test_db():
    """Create a test database"""
    # Use an in-memory SQLite database for testing
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    # Create all tables in the correct order to handle foreign keys
    # Import all models to ensure they are registered with Base
    from app.models import product, video
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create a session
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def db(test_db):
    """Create a database session for each test"""
    # Begin a transaction
    test_db.begin()
    yield test_db
    # Rollback the transaction after each test
    test_db.rollback()