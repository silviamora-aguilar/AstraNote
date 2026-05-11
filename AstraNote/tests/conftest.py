"""
Shared pytest configuration and fixtures for all tests.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# Update these as your models are created
# from src.app.models import Base
# from src.main import app, get_db


@pytest.fixture(scope="session")
def db_engine():
    """Create in-memory SQLite database for testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    # Uncomment when models are defined
    # Base.metadata.create_all(bind=engine)
    yield engine


@pytest.fixture(scope="function")
def db_session(db_engine):
    """Create a fresh database session for each test."""
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=db_engine
    )
    session = TestingSessionLocal()
    
    # Uncomment when models are defined
    # Base.metadata.create_all(bind=db_engine)
    
    yield session
    
    session.close()
    # Base.metadata.drop_all(bind=db_engine)


@pytest.fixture
def client(db_session):
    """FastAPI TestClient with dependency override for database."""
    # Uncomment when app and get_db are available
    # def override_get_db():
    #     try:
    #         yield db_session
    #     finally:
    #         db_session.close()
    #
    # app.dependency_overrides[get_db] = override_get_db
    # 
    # with TestClient(app) as test_client:
    #     yield test_client
    #
    # app.dependency_overrides.clear()
    
    # Placeholder: returns TestClient with no overrides yet
    from src.main import app
    return TestClient(app)


@pytest.fixture
def authenticated_client(client):
    """TestClient with an authenticated user session."""
    # Uncomment when authentication is implemented
    # response = client.post(
    #     "/api/auth/login",
    #     json={"email": "test@example.com", "password": "SecurePassword123"}
    # )
    # assert response.status_code == 200
    # return client
    
    return client


# Markers for test categorization
def pytest_configure(config):
    """Register custom pytest markers."""
    config.addinivalue_line("markers", "unit: mark test as a unit test")
    config.addinivalue_line("markers", "integration: mark test as an integration test")
    config.addinivalue_line("markers", "feature: mark test as a feature/BDD test")
    config.addinivalue_line("markers", "slow: mark test as slow running")
