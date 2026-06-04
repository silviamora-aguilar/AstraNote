"""Shared pytest configuration and fixtures for all tests."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.app.dependencies import (
    get_app_logger,
    get_config_service,
    get_crypto_service,
    get_note_repository,
    get_note_service,
    get_pin_settings_manager,
    get_unlock_session_manager,
)
from src.app.repositories import SqlNoteRepository

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
def client(tmp_path):
    """FastAPI TestClient with a fresh temporary SQLite database per test."""
    import os

    from src.main import app
    from src.app.dependencies import (
        get_app_logger as get_logger_cached,
        get_config_service as get_config_cached,
        get_crypto_service as get_crypto_cached,
        get_note_repository as get_repo_cached,
        get_pin_settings_manager as get_pin_cached,
        get_unlock_session_manager as get_unlock_cached,
    )

    db_path = Path(tmp_path) / "astranote_test.db"
    config_path = Path(tmp_path) / "config.json"
    os.environ["ASTRANOTE_CONFIG_PATH"] = str(config_path)

    # Ensure lru-cached providers do not leak state between tests.
    get_config_cached.cache_clear()
    get_logger_cached.cache_clear()
    get_repo_cached.cache_clear()
    get_crypto_cached.cache_clear()
    get_unlock_cached.cache_clear()
    get_pin_cached.cache_clear()

    shared_crypto = get_crypto_cached()
    repository = SqlNoteRepository(database_url=f"sqlite:///{db_path}", crypto_service=shared_crypto)
    app.dependency_overrides[get_note_repository] = lambda: repository

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    get_config_cached.cache_clear()
    get_logger_cached.cache_clear()
    get_repo_cached.cache_clear()
    get_crypto_cached.cache_clear()
    get_unlock_cached.cache_clear()
    get_pin_cached.cache_clear()
    os.environ.pop("ASTRANOTE_CONFIG_PATH", None)
    repository.engine.dispose()


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
