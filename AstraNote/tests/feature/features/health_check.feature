Feature: Health Check
  Scenario: API returns healthy status
    Given the API is running
    When I call the /health endpoint
    Then I should receive a 200 status
    And the response should contain {"status": "ok"}
