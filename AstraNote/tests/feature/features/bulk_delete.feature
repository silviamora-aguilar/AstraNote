Feature: Bulk Delete Notes
  Scenario: Delete selected notes and keep unselected notes
    Given the API is running
    And I created three notes for bulk delete testing
    When I bulk delete two selected notes
    Then the bulk delete response should be successful
    And exactly two notes should be deleted
    And the unselected note should still be active
