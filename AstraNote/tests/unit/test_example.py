import pytest

@pytest.mark.unit
def test_health_check_response():
    """Test that the /health endpoint returns expected response."""
    from src.main import app
    from fastapi.testclient import TestClient
    
    client = TestClient(app)
    response = client.get("/health")
    
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": "0.1.0"}
