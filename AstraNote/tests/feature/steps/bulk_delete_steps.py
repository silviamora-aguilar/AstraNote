"""Step definitions for BL-03.1 bulk delete feature."""

from behave import given, when, then


@given("I created three notes for bulk delete testing")
def step_create_three_notes(context):
    context.created_notes = []
    for idx in range(3):
        response = context.client.post(
            "/api/notes",
            json={"title": f"BDD Bulk Note {idx}", "body": f"Body {idx}", "is_private": False},
        )
        assert response.status_code == 201, f"Expected create 201, got {response.status_code}"
        context.created_notes.append(response.json())


@when("I bulk delete two selected notes")
def step_bulk_delete_two_notes(context):
    note_ids = [context.created_notes[0]["note_id"], context.created_notes[2]["note_id"]]
    context.bulk_delete_response = context.client.post(
        "/api/notes/bulk-delete",
        json={"note_ids": note_ids},
    )


@then("the bulk delete response should be successful")
def step_bulk_delete_success(context):
    assert context.bulk_delete_response.status_code == 200, (
        f"Expected 200, got {context.bulk_delete_response.status_code}"
    )


@then("exactly two notes should be deleted")
def step_bulk_delete_count(context):
    payload = context.bulk_delete_response.json()
    assert payload["deleted_count"] == 2, f"Expected 2 deleted, got {payload['deleted_count']}"


@then("the unselected note should still be active")
def step_unselected_note_still_active(context):
    remaining_note_id = context.created_notes[1]["note_id"]
    delete_response = context.client.delete(f"/api/notes/{remaining_note_id}")
    assert delete_response.status_code == 204, (
        f"Expected unselected note to remain active; delete returned {delete_response.status_code}"
    )
