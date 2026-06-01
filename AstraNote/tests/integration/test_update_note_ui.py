"""Integration tests for BL-02 dedicated editor-panel HTMX flow."""

from __future__ import annotations

from datetime import datetime, timezone
import re
from uuid import uuid4

import pytest

from src.app.api.notes_ui import _format_created_pacific, _format_modified_pacific


@pytest.mark.integration
def test_htmx_get_editor_panel_renders_selected_note(client) -> None:
    seed_title = f"UI Update Seed {uuid4()}"
    create_response = client.post(
        "/ui/notes",
        data={"title": seed_title, "body": "before", "is_private": "false"},
    )
    assert create_response.status_code == 201

    match = re.search(r'id="note-([a-zA-Z0-9-]+)"', create_response.text)
    assert match is not None
    note_id = match.group(1)

    panel_response = client.get(f"/ui/notes/{note_id}/editor")

    assert panel_response.status_code == 200
    assert "Edit Note" in panel_response.text
    assert seed_title in panel_response.text
    assert "Save edits" in panel_response.text
    assert "name=\"is_private\"" in panel_response.text
    assert "Body formatting tools" in panel_response.text
    assert f"applyWysiwygFormat('bold', 'body-{note_id}')" in panel_response.text
    assert f"id=\"body-{note_id}\"" in panel_response.text
    assert "body-wysiwyg" in panel_response.text


@pytest.mark.integration
def test_notes_page_uses_list_selection_not_inline_dropdown_editor(client) -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "id=\"editor-slot\"" in response.text
    assert "Edit note" not in response.text


@pytest.mark.integration
def test_create_panel_template_includes_formatting_toolbar(client) -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "Body formatting tools" in response.text
    assert "data-format-action=\"bullet\"" in response.text
    assert "data-format-action=\"checklist\"" in response.text
    assert "data-format-action=\"bold\"" in response.text
    assert "data-format-action=\"italic\"" in response.text
    assert "data-format-action=\"underline\"" in response.text
    assert "class=\"body-wysiwyg\"" in response.text


@pytest.mark.integration
def test_htmx_update_note_returns_updated_editor_panel(client) -> None:
    seed_title = f"UI Update Seed {uuid4()}"
    create_response = client.post(
        "/ui/notes",
        data={"title": seed_title, "body": "before", "is_private": "false"},
    )
    assert create_response.status_code == 201

    match = re.search(r'id="note-([a-zA-Z0-9-]+)"', create_response.text)
    assert match is not None
    note_id = match.group(1)

    update_response = client.post(
        f"/ui/notes/{note_id}/editor",
        data={"title": "Updated via UI", "body": "after"},
    )

    assert update_response.status_code == 200
    assert "Updated via UI" in update_response.text
    assert "Save edits" in update_response.text
    assert "hx-swap-oob=\"outerHTML\"" in update_response.text
    assert "Created:" in update_response.text
    assert "PDT" in update_response.text


@pytest.mark.integration
def test_htmx_update_note_returns_inline_error_for_invalid_title(client) -> None:
    create_response = client.post(
        "/ui/notes",
        data={"title": f"UI Invalid Seed {uuid4()}", "body": "before", "is_private": "false"},
    )
    assert create_response.status_code == 201

    match = re.search(r'id="note-([a-zA-Z0-9-]+)"', create_response.text)
    assert match is not None
    note_id = match.group(1)

    update_response = client.post(
        f"/ui/notes/{note_id}/editor",
        data={"title": "bad<title", "body": "after"},
    )

    assert update_response.status_code == 200
    assert "unsupported symbols" in update_response.text
    assert 'value="bad&lt;title"' in update_response.text
    assert 'value="after"' in update_response.text


@pytest.mark.integration
def test_htmx_update_note_returns_404_error_partial_for_missing_note(client) -> None:
    response = client.post(
        "/ui/notes/missing-note-id/editor",
        data={"title": "Any Title", "body": "x"},
    )

    assert response.status_code == 404
    assert "Note not found" in response.text


@pytest.mark.integration
def test_htmx_update_note_clears_body_when_body_field_missing(client) -> None:
    create_response = client.post(
        "/ui/notes",
        data={"title": f"Body Preserve Seed {uuid4()}", "body": "kept body", "is_private": "false"},
    )
    assert create_response.status_code == 201

    match = re.search(r'id="note-([a-zA-Z0-9-]+)"', create_response.text)
    assert match is not None
    note_id = match.group(1)

    update_response = client.post(
        f"/ui/notes/{note_id}/editor",
        data={"title": "Updated title only"},
    )

    assert update_response.status_code == 200
    assert "Updated title only" in update_response.text
    assert "kept body" not in update_response.text


@pytest.mark.integration
def test_private_note_list_item_shows_private_placeholder(client) -> None:
    response = client.post(
        "/ui/notes",
        data={"title": f"Private Preview Seed {uuid4()}", "body": "secret text", "is_private": "true"},
    )

    assert response.status_code == 201
    assert "Private note" in response.text
    assert "secret text" not in response.text


@pytest.mark.integration
def test_public_empty_note_list_item_shows_empty_placeholder(client) -> None:
    response = client.post(
        "/ui/notes",
        data={"title": f"Empty Preview Seed {uuid4()}", "body": "", "is_private": "false"},
    )

    assert response.status_code == 201
    assert "Note is empty" in response.text


@pytest.mark.integration
def test_notes_page_includes_today_note_target(client) -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "id=\"today-note-list\"" in response.text


@pytest.mark.integration
def test_notes_page_renders_today_group_for_new_note(client) -> None:
    create_response = client.post(
        "/ui/notes",
        data={"title": f"Today Group Seed {uuid4()}", "body": "today body", "is_private": "false"},
    )
    assert create_response.status_code == 201

    page_response = client.get("/")
    assert page_response.status_code == 200
    assert "Today" in page_response.text


@pytest.mark.integration
def test_note_preview_returns_full_content_for_css_ellipsis(client) -> None:
    long_body = "A" * 260
    response = client.post(
        "/ui/notes",
        data={"title": f"Preview Truncate Seed {uuid4()}", "body": long_body, "is_private": "false"},
    )

    assert response.status_code == 201
    assert long_body in response.text


@pytest.mark.integration
def test_note_preview_renders_only_first_line(client) -> None:
    response = client.post(
        "/ui/notes",
        data={
            "title": f"First Line Preview Seed {uuid4()}",
            "body": "first line only\nsecond line should not appear",
            "is_private": "false",
        },
    )

    assert response.status_code == 201
    assert "first line only" in response.text
    assert "second line should not appear" not in response.text


@pytest.mark.integration
def test_note_preview_skips_blank_leading_lines(client) -> None:
    response = client.post(
        "/ui/notes",
        data={
            "title": f"Blank Lead Preview Seed {uuid4()}",
            "body": "\n\nactual first content\nnext line content",
            "is_private": "false",
        },
    )

    assert response.status_code == 201
    assert "actual first content" in response.text
    assert "next line content" not in response.text


@pytest.mark.integration
def test_note_preview_renders_checklist_visual_not_markdown(client) -> None:
    response = client.post(
        "/ui/notes",
        data={
            "title": f"Checklist Preview Seed {uuid4()}",
            "body": "- [x] done task\nnext line",
            "is_private": "false",
        },
    )

    assert response.status_code == 201
    assert "note-preview-checkbox is-checked" in response.text
    assert "done task" in response.text
    assert "- [x] done task" not in response.text


@pytest.mark.integration
def test_note_preview_renders_inline_italic_from_first_line(client) -> None:
    response = client.post(
        "/ui/notes",
        data={
            "title": f"Italic Preview Seed {uuid4()}",
            "body": "*focus text*\nplain second line",
            "is_private": "false",
        },
    )

    assert response.status_code == 201
    assert "<em>focus text</em>" in response.text


@pytest.mark.integration
def test_note_title_is_truncated_to_40_chars_with_ellipsis(client) -> None:
    long_title = "T" * 65
    response = client.post(
        "/ui/notes",
        data={"title": long_title, "body": "short body", "is_private": "false"},
    )

    assert response.status_code == 201
    assert 'class="note-select"' in response.text
    assert 'data-full-title="' in response.text
    assert ("T" * 37 + "...") in response.text


@pytest.mark.integration
def test_note_list_item_does_not_render_created_date(client) -> None:
    response = client.post(
        "/ui/notes",
        data={"title": f"No Date Seed {uuid4()}", "body": "date body", "is_private": "false"},
    )

    assert response.status_code == 201
    assert "<span class=\"note-meta\">" not in response.text


@pytest.mark.integration
def test_editor_panel_renders_modified_timestamp_under_created(client) -> None:
    create_response = client.post(
        "/ui/notes",
        data={"title": f"Modified Stamp Seed {uuid4()}", "body": "before", "is_private": "false"},
    )
    assert create_response.status_code == 201

    match = re.search(r'id="note-([a-zA-Z0-9-]+)"', create_response.text)
    assert match is not None
    note_id = match.group(1)

    editor_response = client.get(f"/ui/notes/{note_id}/editor")
    assert editor_response.status_code == 200
    assert re.search(r"Modified:\s*[A-Z][a-z]+\s\d{2},\s\d{4}\s\d{2}:\d{2}\s(?:AM|PM)\s(PST|PDT)", editor_response.text)


@pytest.mark.integration
def test_created_timestamp_label_switches_between_pst_and_pdt() -> None:
    summer_timestamp = datetime(2026, 5, 18, 23, 0, 0, tzinfo=timezone.utc)
    winter_timestamp = datetime(2026, 1, 18, 23, 0, 0, tzinfo=timezone.utc)

    assert _format_created_pacific(summer_timestamp).endswith("PDT")
    assert _format_created_pacific(winter_timestamp).endswith("PST")


@pytest.mark.integration
def test_modified_timestamp_label_switches_between_pst_and_pdt() -> None:
    summer_timestamp = datetime(2026, 5, 18, 23, 0, 0, tzinfo=timezone.utc)
    winter_timestamp = datetime(2026, 1, 18, 23, 0, 0, tzinfo=timezone.utc)

    assert _format_modified_pacific(summer_timestamp).endswith("PDT")
    assert _format_modified_pacific(winter_timestamp).endswith("PST")


@pytest.mark.integration
def test_editor_panel_renders_checklist_toggle_controls(client) -> None:
    create_response = client.post(
        "/ui/notes",
        data={"title": f"Checklist Seed {uuid4()}", "body": "- [ ] first task\n- [x] second task", "is_private": "false"},
    )
    assert create_response.status_code == 201

    match = re.search(r'id="note-([a-zA-Z0-9-]+)"', create_response.text)
    assert match is not None
    note_id = match.group(1)

    editor_response = client.get(f"/ui/notes/{note_id}/editor")
    assert editor_response.status_code == 200
    assert "Checklist" in editor_response.text
    assert "body-wysiwyg" in editor_response.text
    assert f"body-hidden-{note_id}" in editor_response.text


@pytest.mark.integration
def test_checklist_toggle_route_persists_state_and_returns_updated_panel(client) -> None:
    create_response = client.post(
        "/ui/notes",
        data={"title": f"Checklist Toggle {uuid4()}", "body": "- [ ] first task\n- [x] second task", "is_private": "false"},
    )
    assert create_response.status_code == 201

    match = re.search(r'id="note-([a-zA-Z0-9-]+)"', create_response.text)
    assert match is not None
    note_id = match.group(1)

    toggle_response = client.post(
        f"/ui/notes/{note_id}/checklist-toggle",
        data={"line_index": "0", "checked": "true"},
    )
    assert toggle_response.status_code == 200
    assert "- [x] first task" in toggle_response.text

    api_response = client.get("/api/notes/search", params={"q": "first task"})
    assert api_response.status_code == 200
    matching_note = next((item for item in api_response.json() if item["note_id"] == note_id), None)
    assert matching_note is not None
    assert "- [x] first task" in matching_note["body"]


@pytest.mark.integration
def test_checklist_toggle_route_returns_400_for_invalid_index(client) -> None:
    create_response = client.post(
        "/ui/notes",
        data={"title": f"Checklist Invalid {uuid4()}", "body": "- [ ] first task", "is_private": "false"},
    )
    assert create_response.status_code == 201

    match = re.search(r'id="note-([a-zA-Z0-9-]+)"', create_response.text)
    assert match is not None
    note_id = match.group(1)

    toggle_response = client.post(
        f"/ui/notes/{note_id}/checklist-toggle",
        data={"line_index": "2", "checked": "true"},
    )
    assert toggle_response.status_code == 400
    assert "out of range" in toggle_response.text
