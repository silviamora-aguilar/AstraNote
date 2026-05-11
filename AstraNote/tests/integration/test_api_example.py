# Sample Integration Test - Demonstrates API Testing Pattern
# Run with: pytest tests/integration/test_api_example.py -v

import pytest
from fastapi.testclient import TestClient
from src.main import app

@pytest.mark.integration
def test_health_endpoint_integration():
    """Test /health endpoint through full FastAPI request cycle."""
    client = TestClient(app)
    response = client.get("/health")
    
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

@pytest.mark.integration
def test_not_found_endpoint():
    """Test that undefined routes return 404."""
    client = TestClient(app)
    response = client.get("/api/nonexistent")
    
    assert response.status_code == 404
