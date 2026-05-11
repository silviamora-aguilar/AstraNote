# Sample Unit Test - Demonstrates TDD Pattern
# Run with: pytest tests/unit/test_example.py -v

import pytest

@pytest.mark.unit
def test_example_placeholder():
    """
    Placeholder test to demonstrate project structure.
    
    Replace this with actual unit tests for:
    - NoteService CRUD operations
    - PasswordHash verification
    - KeyDerivation (PIN → encryption key)
    - Repository database queries
    """
    assert True

@pytest.mark.unit
def test_health_check_response():
    """Test that the /health endpoint returns expected response."""
    from src.main import app
    from fastapi.testclient import TestClient
    
    client = TestClient(app)
    response = client.get("/health")
    
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
