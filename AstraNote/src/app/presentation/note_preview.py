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
        checkbox_class = f"note-preview-checkbox{' is-checked' if checked else ''}"
        text_class = f"note-preview-text{' is-checked' if checked else ''}"
        return Markup(
            '<span class="note-preview-row note-preview-row-checklist">'
            f'<span class="{checkbox_class}" aria-hidden="true"></span>'
            f'<span class="{text_class}">{label}</span>'
            "</span>"
        )

    if unicode_checklist_match is not None:
        checked = unicode_checklist_match.group(1) == "☑"
        label = _render_inline_formatting(unicode_checklist_match.group(2).strip())
        checkbox_class = f"note-preview-checkbox{' is-checked' if checked else ''}"
        text_class = f"note-preview-text{' is-checked' if checked else ''}"
        return Markup(
            '<span class="note-preview-row note-preview-row-checklist">'
            f'<span class="{checkbox_class}" aria-hidden="true"></span>'
            f'<span class="{text_class}">{label}</span>'
            "</span>"
        )

    bullet_match = BULLET_LINE_RE.match(first_line)
    if bullet_match is not None:
        label = _render_inline_formatting(bullet_match.group(1).strip())
        return Markup(
            '<span class="note-preview-row note-preview-row-bullet">'
            '<span class="note-preview-bullet" aria-hidden="true">•</span>'
            f'<span class="note-preview-text">{label}</span>'
            "</span>"
        )

    rendered_first_line = _render_inline_formatting(first_line)
    return Markup(f'<span class="note-preview-text">{rendered_first_line}</span>')


def render_note_body_html(body: str) -> Markup:
    """Render full note body with checklist/bullet/inline formatting for read-only display."""
    lines = (body or "").split("\n")
    html: list[str] = []
    idx = 0

    while idx < len(lines):
        line = lines[idx]
        checklist_match = CHECKLIST_LINE_RE.match(line) or UNICODE_CHECKLIST_LINE_RE.match(line)
        bullet_match = None if checklist_match else BULLET_LINE_RE.match(line)

        if checklist_match is not None:
            html.append('<ul class="editor-checklist">')
            while idx < len(lines):
                inner = lines[idx]
                markdown_match = CHECKLIST_LINE_RE.match(inner)
                unicode_match = UNICODE_CHECKLIST_LINE_RE.match(inner)
                if markdown_match is None and unicode_match is None:
                    break

                if markdown_match is not None:
                    checked = markdown_match.group(1).lower() == "x"
                    label = _render_inline_formatting(markdown_match.group(2).strip())
                else:
                    assert unicode_match is not None
                    checked = unicode_match.group(1) == "☑"
                    label = _render_inline_formatting(unicode_match.group(2).strip())

                html.append(
                    f'<li{" class=\"is-checked\"" if checked else ""}>'
                    f'<input type="checkbox" contenteditable="false"'
                    f'{" checked" if checked else ""} disabled>'
                    f"<span>{label}</span>"
                    "</li>"
                )
                idx += 1
            html.append("</ul>")
            continue

        if bullet_match is not None:
            html.append('<ul class="editor-bullets">')
            while idx < len(lines):
                inner = lines[idx]
                bullet_line_match = BULLET_LINE_RE.match(inner)
                if bullet_line_match is None:
                    break
                html.append(
                    f"<li>{_render_inline_formatting(bullet_line_match.group(1).strip())}</li>"
                )
                idx += 1
            html.append("</ul>")
            continue

        if line.strip() == "":
            html.append("<div><br></div>")
            idx += 1
            continue

        html.append(f"<div>{_render_inline_formatting(line)}</div>")
        idx += 1

    return Markup("".join(html))
