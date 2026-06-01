"""Render note-preview HTML for first-line note list snippets."""

from __future__ import annotations

import re

from markupsafe import Markup, escape

CHECKLIST_LINE_RE = re.compile(r"^\s*[-*+]\s+\[( |x|X)\]\s+(.*)$")
UNICODE_CHECKLIST_LINE_RE = re.compile(r"^\s*(☐|☑)\s+(.*)$")
BULLET_LINE_RE = re.compile(r"^\s*(?:•|[-*+])\s+(?!\[(?: |x|X)\]\s+)(.*)$")
UNDERLINE_RE = re.compile(r"&lt;u&gt;(.*?)&lt;/u&gt;", re.IGNORECASE)
BOLD_RE = re.compile(r"\*\*(.+?)\*\*")
ITALIC_RE = re.compile(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)")


def _render_inline_formatting(text: str) -> str:
    escaped = str(escape(text))
    escaped = UNDERLINE_RE.sub(r"<u>\1</u>", escaped)
    escaped = BOLD_RE.sub(r"<strong>\1</strong>", escaped)
    escaped = ITALIC_RE.sub(r"<em>\1</em>", escaped)
    return escaped


def render_note_preview_html(body: str) -> Markup:
    """Render preview as first-line formatted HTML for note-list cards."""
    first_line = ""
    for line in (body or "").splitlines():
        candidate = line.strip()
        if candidate:
            first_line = candidate
            break
    if not first_line:
        return Markup("")

    checklist_match = CHECKLIST_LINE_RE.match(first_line)
    unicode_checklist_match = UNICODE_CHECKLIST_LINE_RE.match(first_line)
    if checklist_match is not None:
        checked = checklist_match.group(1).lower() == "x"
        label = _render_inline_formatting(checklist_match.group(2).strip())
        return Markup(
            "<span class=\"note-preview-row note-preview-row-checklist\">"
            f"<span class=\"note-preview-checkbox{' is-checked' if checked else ''}\" aria-hidden=\"true\"></span>"
            f"<span class=\"note-preview-text{' is-checked' if checked else ''}\">{label}</span>"
            "</span>"
        )

    if unicode_checklist_match is not None:
        checked = unicode_checklist_match.group(1) == "☑"
        label = _render_inline_formatting(unicode_checklist_match.group(2).strip())
        return Markup(
            "<span class=\"note-preview-row note-preview-row-checklist\">"
            f"<span class=\"note-preview-checkbox{' is-checked' if checked else ''}\" aria-hidden=\"true\"></span>"
            f"<span class=\"note-preview-text{' is-checked' if checked else ''}\">{label}</span>"
            "</span>"
        )

    bullet_match = BULLET_LINE_RE.match(first_line)
    if bullet_match is not None:
        label = _render_inline_formatting(bullet_match.group(1).strip())
        return Markup(
            "<span class=\"note-preview-row note-preview-row-bullet\">"
            "<span class=\"note-preview-bullet\" aria-hidden=\"true\">•</span>"
            f"<span class=\"note-preview-text\">{label}</span>"
            "</span>"
        )

    return Markup(f"<span class=\"note-preview-text\">{_render_inline_formatting(first_line)}</span>")
