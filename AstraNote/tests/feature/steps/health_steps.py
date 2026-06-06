"""Step definitions for health check feature."""

from behave import given, when, then
from fastapi.testclient import TestClient
from src.main import app


@given("the API is running")
def step_api_running(context):
    """Initialize API test client."""
    context.client = TestClient(app)


@when("I call the /health endpoint")
def step_call_health(context):
    """Call the /health endpoint."""
    context.response = context.client.get("/health")


@then("I should receive a 200 status")
def step_check_status(context):
    """Verify response status is 200."""
    assert context.response.status_code == 200, f"Expected 200, got {context.response.status_code}"


@then("the response should contain {expected_json}")
def step_check_json(context, expected_json):
    """Verify response JSON matches expected."""
    import json

    expected = json.loads(expected_json)
    actual = context.response.json()
    for key, value in expected.items():
        assert actual.get(key) == value, f"Expected {key}={value}, got {actual}"
