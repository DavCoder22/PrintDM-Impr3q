import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

# Use an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create the test database and tables
Base.metadata.create_all(bind=engine)

def override_get_db():
    """Override the get_db dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

@pytest.fixture(scope="module")
def test_app():
    """Create a test client that uses the override_get_db fixture"""
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture(scope="module")
def db_session():
    """Create a new database session with a rollback at the end of the test"""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client():
    """Create a test client for the FastAPI application."""
    return TestClient(app)

# Mock HTTP client for external service calls
@pytest.fixture
def mock_http_client():
    """Create a mock HTTP client for testing external service calls."""
    with patch("httpx.AsyncClient") as mock:
        mock_client = AsyncMock()
        mock.return_value.__aenter__.return_value = mock_client
        yield mock_client

# Test data fixtures
@pytest.fixture
def test_printer():
    """Return a test printer dictionary."""
    return {
        "id": "printer-1",
        "name": "Test Printer",
        "status": "idle",
        "ip_address": "192.168.1.100"
    }

@pytest.fixture
def test_job():
    """Return a test print job dictionary."""
    return {
        "id": "job-123",
        "printer_id": "printer-1",
        "file_name": "test.gcode",
        "file_size": 1024,
        "estimated_duration": 3600,
        "status": "queued",
        "progress": 0.0,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }

@pytest.fixture
def test_alert():
    """Return a test alert dictionary."""
    return {
        "id": "alert-123",
        "printer_id": "printer-1",
        "level": "warning",
        "message": "Test alert",
        "details": {"temperature": 85},
        "status": "open",
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }

@pytest.fixture
def test_metric():
    """Return a test metric dictionary."""
    return {
        "id": "metric-123",
        "printer_id": "printer-1",
        "metric_type": "temperature",
        "value": 75.5,
        "timestamp": datetime.utcnow().isoformat()
    }
