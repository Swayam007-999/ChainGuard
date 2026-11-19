"""Pytest fixtures for testing ChainGuard backend."""

import os
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

# Ensure test environment variables are set before app imports
os.environ["CHAINGUARD_API_KEY"] = "test_secret_api_key_for_testing_12345678"
os.environ["ADMIN_PASSWORD"] = "test_admin_password_strong_123"
os.environ["JWT_SECRET"] = "test_jwt_secret_key_minimum_32_characters_12345"
os.environ["FINGERPRINT_KEY"] = "test_fingerprint_hmac_secret_key_12345"
os.environ["DEBUG"] = "true"

from app.auth import create_access_token
from app.config import settings
from app.database import Base, get_db
from app.main import app
from app.rate_limiter import rate_limiter

# In-memory SQLite database specifically for test runs
TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(autouse=True)
def setup_database() -> Generator[None, None, None]:
    """Create all database tables before each test and drop them after."""
    Base.metadata.create_all(bind=test_engine)
    rate_limiter.reset()  # Reset in-memory rate limiter buckets
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    """Provide a clean database session for test assertions."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """Provide a FastAPI TestClient with the database dependency overridden."""
    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def valid_api_headers() -> dict:
    """Header dict with the correct X-ChainGuard-Key."""
    return {"X-ChainGuard-Key": settings.CHAINGUARD_API_KEY}


@pytest.fixture
def invalid_api_headers() -> dict:
    """Header dict with an incorrect API key."""
    return {"X-ChainGuard-Key": "wrong_and_malicious_api_key_value"}


@pytest.fixture
def admin_cookie() -> dict:
    """Cookie dict with a valid admin JWT."""
    token = create_access_token({"sub": "admin", "role": "admin"})
    return {"access_token": token}
