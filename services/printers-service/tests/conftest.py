import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app, get_db
from app.database import Base

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# Create test database tables
Base.metadata.create_all(bind=test_engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

@pytest.fixture(scope="module")
def test_app():
    # Override the database dependency for testing
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    # Clean up after tests
    app.dependency_overrides.clear()

@pytest.fixture(scope="module")
def test_db():
    # Create a new database session for testing
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Clear all data after each test module
        Base.metadata.drop_all(bind=test_engine)
        Base.metadata.create_all(bind=test_engine)
