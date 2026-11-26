from io import BytesIO
from pathlib import Path
import fcntl
import hashlib
import json
import os
import re
import tempfile
from xml.sax.saxutils import escape

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST
from django.utils.safestring import mark_safe
import markdown


from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    ListFlowable, ListItem, Preformatted,
)


@login_required
def user_guide(request):
    """Role-independent user documentation for all authenticated users."""
    return render(request, "meetings/user_guide.html")


@login_required
def security_description(request):
    """Show the complete IT, security and privacy assessment as a separate help page."""
    source = Path(settings.BASE_DIR) / "docs" / "Funktions-und-Sicherheitsbeschreibung.md"
    if not source.is_file():
        return HttpResponse("Die Sicherheitsbeschreibung ist derzeit nicht verfügbar.", status=404)
    parser = markdown.Markdown(
        extensions=["tables", "fenced_code", "sane_lists", "toc"],
        output_format="html5",
    )
    content = parser.convert(source.read_text(encoding="utf-8"))
    return render(request, "meetings/security_description.html", {
        "security_description_html": mark_safe(content),
        "security_description_toc_html": mark_safe(parser.toc),
    })


def _test_documentation_testing_mode_enabled():
    """Use the same deployment-level TESTING switch as the update interface."""
    from .views import _debian_testing_mode_enabled
    return _debian_testing_mode_enabled()


def _test_documentation_source_path():
    configured_path = os.getenv("TEST_DOCUMENTATION_SOURCE_PATH")
    if configured_path:
        return Path(configured_path)
    return Path(settings.BASE_DIR) / "docs" / "Pruefung-des-Verfahrens-Testdokumentation.md"


def _test_documentation_lock_path(source=None):
    """Return the configured lock identifier shared with the deployment updater."""
    configured_path = os.getenv("TEST_DOCUMENTATION_LOCK_PATH")
    if configured_path:
        return Path(configured_path)
    source = source or _test_documentation_source_path()
    return source.with_name(source.name + ".lock")


def _test_documentation_lock_directory(source=None):
    """Use the lock file's parent directory as the shared OS-level lock.

    Locking the directory avoids opening or modifying a stale lock file whose
    owner, mode, ACL, or filesystem attributes may prevent access during deploy.
    """
    return _test_documentation_lock_path(source).parent


def _render_test_documentation_markers(markdown_source, editable):
    """Render Markdown checkbox markers as controls, editable only in TESTING mode."""
    rendered_lines = []
    for line_number, line in enumerate(markdown_source.splitlines(keepends=True), start=1):
        occurrence = 0

        def render_checkbox(match):
            nonlocal occurrence
            occurrence += 1
            checked_attribute = " checked" if match.group(1).lower() == "x" else ""
            disabled_attribute = "" if editable else " disabled"
            return (
                '<input type="checkbox" class="test-checklist-box'
                + (' test-success-checkbox' if "**Test erfolgreich:**" in line else '') + '" '
                f'data-checklist-line="{line_number}" '
                f'data-checklist-occurrence="{occurrence}"'
                f'{checked_attribute}{disabled_attribute}>'
            )

        rendered_lines.append(re.sub(r"\[([ xX])\]", render_checkbox, line))
    return "".join(rendered_lines)


def _checklist_revision(content):
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _checklist_status(content):
    statuses = {}
    for line_number, line in enumerate(content.splitlines(), start=1):
        occurrence = 0
        for match in re.finditer(r"\[([ xX])\]", line):
            occurrence += 1
            statuses[f"line-{line_number}-{occurrence}"] = match.group(1).lower() == "x"
    return statuses


def _write_checklist_atomically(source, content):
    """Replace the Markdown file atomically while preserving its file mode."""
    original_mode = source.stat().st_mode
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", newline="", dir=source.parent,
            prefix=f".{source.name}.", suffix=".tmp", delete=False,
        ) as temporary:
            temporary_path = Path(temporary.name)
            temporary.write(content)
            temporary.flush()
            os.fsync(temporary.fileno())
        os.chmod(temporary_path, original_mode)
        os.replace(temporary_path, source)
    finally:
        if temporary_path and temporary_path.exists():
            temporary_path.unlink()


@login_required
def test_documentation(request):
    """Render the shared server-local Markdown checklist."""
    source = _test_documentation_source_path()
    if not source.is_file():
        return HttpResponse("Die Testcheckliste ist derzeit nicht verfügbar.", status=404)

    markdown_source = source.read_text(encoding="utf-8")
    testing_mode = _test_documentation_testing_mode_enabled()
    rendered_source = _render_test_documentation_markers(markdown_source, testing_mode)
    parser = markdown.Markdown(
        extensions=["tables", "fenced_code", "sane_lists", "toc"],
        output_format="html5",
    )
    content = parser.convert(rendered_source)
    return render(request, "meetings/test_documentation.html", {
        "test_documentation_html": mark_safe(content),
        "test_documentation_toc_html": mark_safe(parser.toc),
        "test_documentation_revision": _checklist_revision(markdown_source),
        "test_documentation_editable": testing_mode,
    })


@login_required
@require_GET
def test_documentation_status(request):
    """Return the current shared checklist state for live refresh in open sessions."""
    if not _test_documentation_testing_mode_enabled():
        return JsonResponse({"error": "TESTING-Modus ist nicht aktiv."}, status=403)
    source = _test_documentation_source_path()
    if not source.is_file():
        return JsonResponse({"error": "Testcheckliste nicht verfügbar."}, status=404)
    content = source.read_text(encoding="utf-8")
    return JsonResponse({
        "revision": _checklist_revision(content),
        "statuses": _checklist_status(content),
    })


@login_required
@require_POST
def test_documentation_toggle(request):
    """Persist one checkbox directly in the local Markdown file."""
    if not _test_documentation_testing_mode_enabled():
        return JsonResponse({"error": "TESTING-Modus ist nicht aktiv."}, status=403)
    try:
        payload = json.loads(request.body.decode("utf-8"))
        if not isinstance(payload, dict):
            return JsonResponse({"error": "Ungültige Anfrage."}, status=400)
        line_number = int(payload.get("line", 0))
        occurrence = int(payload.get("occurrence", 0))
        checked = payload.get("checked")
        revision = payload.get("revision")
    except (ValueError, TypeError, UnicodeDecodeError, json.JSONDecodeError):
        return JsonResponse({"error": "Ungültige Anfrage."}, status=400)

    if line_number < 1 or occurrence < 1 or not isinstance(checked, bool):
        return JsonResponse({"error": "Ungültige Checkbox-Angaben."}, status=400)
    if not isinstance(revision, str) or not re.fullmatch(r"[0-9a-f]{64}", revision):
        return JsonResponse({"error": "Ungültige Dokumentversion."}, status=400)

    source = _test_documentation_source_path()
    if not source.is_file():
        return JsonResponse({"error": "Testcheckliste nicht verfügbar."}, status=404)

    lock_directory = _test_documentation_lock_directory(source)
    lock_fd = None
    try:
        lock_fd = os.open(str(lock_directory), os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        fcntl.flock(lock_fd, fcntl.LOCK_EX)
        content = source.read_text(encoding="utf-8")
        current_revision = _checklist_revision(content)
        if revision != current_revision:
            return JsonResponse({
                "error": "Die Checkliste wurde zwischenzeitlich geändert.",
                "revision": current_revision,
                "statuses": _checklist_status(content),
            }, status=409)

        lines = content.splitlines(keepends=True)
        if line_number > len(lines):
            return JsonResponse({"error": "Checkbox nicht gefunden."}, status=400)
        matches = list(re.finditer(r"\[([ xX])\]", lines[line_number - 1]))
        if occurrence > len(matches):
            return JsonResponse({"error": "Checkbox nicht gefunden."}, status=400)
        match = matches[occurrence - 1]
        marker = "[x]" if checked else "[ ]"
        lines[line_number - 1] = (
            lines[line_number - 1][:match.start()] + marker
            + lines[line_number - 1][match.end():]
        )
        updated_content = "".join(lines)
        _write_checklist_atomically(source, updated_content)
        updated_revision = _checklist_revision(updated_content)
        return JsonResponse({
            "success": True,
            "revision": updated_revision,
            "statuses": _checklist_status(updated_content),
        })
    except OSError:
        return JsonResponse({"error": "Die Testcheckliste konnte nicht gespeichert werden."}, status=500)
    finally:
        if lock_fd is not None:
            try:
                fcntl.flock(lock_fd, fcntl.LOCK_UN)
            finally:
                os.close(lock_fd)



@login_required
@require_GET
def test_documentation_download(request):
    """Download the complete, current Markdown source in TESTING mode only."""
    if not _test_documentation_testing_mode_enabled():
        return HttpResponse("Der Markdown-Export ist nur im TESTING-Modus verfügbar.", status=403)
    source = _test_documentation_source_path()
    if not source.is_file():
        return HttpResponse("Die Testcheckliste ist derzeit nicht verfügbar.", status=404)
    response = HttpResponse(source.read_bytes(), content_type="text/markdown; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="Pruefung-des-Verfahrens-Testdokumentation.md"'
    response["Cache-Control"] = "private, no-store"
    response["X-Content-Type-Options"] = "nosniff"
    return response


def _inline_markup(value):
    """Escape Markdown text before translating the small inline subset used in the PDF."""
    value = value.strip()
    # ReportLab's built-in Helvetica fonts use WinAnsi; normalize symbols outside it.
    value = (value.replace("→", "->").replace("←", "<-")
        .replace("☐", "[ ]").replace("☑", "[x]")
        .replace("≥", ">=").replace("≤", "<=").replace("≠", "!=")
        .replace("—", "-").replace("–", "-").replace("…", "..."))
    value = escape(value)
    value = re.sub(r"`([^\`]+)`", r'<font name="Courier" size="8">\1</font>', value)
    value = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", value)
    value = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<i>\1</i>", value)
    return value.replace("\\n", "<br/>")


def _markdown_story(markdown):
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="DocTitle", parent=styles["Title"], fontName="Helvetica-Bold",
        fontSize=20, leading=24, textColor=colors.HexColor("#17365D"),
        alignment=TA_CENTER, spaceAfter=12,
    ))
    styles.add(ParagraphStyle(
        name="DocH1", parent=styles["Heading1"], fontSize=15, leading=18,
        textColor=colors.HexColor("#17365D"), spaceBefore=14, spaceAfter=7,
        keepWithNext=True,
    ))
    styles.add(ParagraphStyle(
        name="DocH2", parent=styles["Heading2"], fontSize=11.5, leading=14,
        textColor=colors.HexColor("#24527A"), spaceBefore=10, spaceAfter=5,
        keepWithNext=True,
    ))
    styles.add(ParagraphStyle(
        name="DocBody", parent=styles["BodyText"], fontSize=8.5, leading=11.5,
        spaceAfter=5,
    ))
    styles.add(ParagraphStyle(
        name="DocSmall", parent=styles["BodyText"], fontSize=7.1, leading=9,
    ))
    styles.add(ParagraphStyle(
        name="DocTableHeader", parent=styles["BodyText"], fontName="Helvetica-Bold",
        fontSize=7.1, leading=9, textColor=colors.white,
    ))
    styles.add(ParagraphStyle(
        name="DocCode", parent=styles["Code"], fontSize=7.2, leading=9,
        backColor=colors.HexColor("#F1F5F9"), borderPadding=5,
    ))

    lines = markdown.splitlines()
    story = []
    i = 0
    first_heading = True
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        if line.startswith("```"):
            i += 1
            block = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                block.append(lines[i])
                i += 1
            story.append(Preformatted("\\n".join(block), styles["DocCode"]))
            story.append(Spacer(1, 5))
            i += 1
            continue
        if line.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                raw = [cell.strip() for cell in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-{3,}:?", cell.replace(" ", "")) for cell in raw):
                    row_style = styles["DocTableHeader"] if not rows else styles["DocSmall"]
                    rows.append([Paragraph(_inline_markup(cell), row_style) for cell in raw])
                i += 1
            if rows:
                columns = max(len(row) for row in rows)
                normalized = [row + [Paragraph("", styles["DocSmall"])] * (columns-len(row)) for row in rows]
                widths = [ (A4[0] - 36*mm) / columns ] * columns
                table = Table(normalized, colWidths=widths, repeatRows=1, hAlign="LEFT")
                table.setStyle(TableStyle([
                    ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#17365D")),
                    ("TEXTCOLOR", (0,0), (-1,0), colors.white),
                    ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
                    ("GRID", (0,0), (-1,-1), 0.35, colors.HexColor("#CBD5E1")),
                    ("VALIGN", (0,0), (-1,-1), "TOP"),
                    ("LEFTPADDING", (0,0), (-1,-1), 4),
                    ("RIGHTPADDING", (0,0), (-1,-1), 4),
                    ("TOPPADDING", (0,0), (-1,-1), 4),
                    ("BOTTOMPADDING", (0,0), (-1,-1), 4),
                    ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#F1F5F9")]),
                ]))
                story.extend([table, Spacer(1, 7)])
            continue
        if line.startswith("# "):
            story.append(Paragraph(_inline_markup(line[2:]), styles["DocTitle"] if first_heading else styles["DocH1"]))
            first_heading = False
            i += 1
            continue
        if line.startswith("## "):
            story.append(Paragraph(_inline_markup(line[3:]), styles["DocH1"]))
            i += 1
            continue
        if line.startswith("### "):
            story.append(Paragraph(_inline_markup(line[4:]), styles["DocH2"]))
            i += 1
            continue
        if line.startswith(">"):
            story.append(Paragraph(_inline_markup(line.lstrip("> ")), styles["DocBody"]))
            i += 1
            continue
        if line.startswith("- ") or re.match(r"\d+\. ", line):
            ordered = bool(re.match(r"\d+\. ", line))
            items = []
            while i < len(lines):
                candidate = lines[i].strip()
                if ordered and re.match(r"\d+\. ", candidate):
                    text = re.sub(r"^\d+\. ", "", candidate)
                elif not ordered and candidate.startswith("- "):
                    text = candidate[2:]
                else:
                    break
                items.append(ListItem(Paragraph(_inline_markup(text), styles["DocBody"]), leftIndent=8))
                i += 1
            story.append(ListFlowable(
                items, bulletType="1" if ordered else "bullet",
                start="1", leftIndent=16, bulletFontSize=7,
            ))
            story.append(Spacer(1, 3))
            continue
        paragraph = [line]
        i += 1
        while i < len(lines):
            candidate = lines[i].strip()
            if not candidate or candidate.startswith(("#", "|", ">", "```", "- ")) or re.match(r"\d+\. ", candidate):
                break
            paragraph.append(candidate)
            i += 1
        story.append(Paragraph(_inline_markup(" ".join(paragraph)), styles["DocBody"]))

    return story


@login_required
def security_description_pdf(request):
    """Build the current security and privacy description as an authenticated PDF download."""
    source = Path(settings.BASE_DIR) / "docs" / "Funktions-und-Sicherheitsbeschreibung.md"
    if not source.is_file():
        return HttpResponse("Die Sicherheitsbeschreibung ist derzeit nicht verfügbar.", status=404)
    buffer = BytesIO()
    document = SimpleDocTemplate(
        buffer, pagesize=A4, rightMargin=18*mm, leftMargin=18*mm,
        topMargin=17*mm, bottomMargin=17*mm,
        title="Meeting Manager – Funktions- und Sicherheitsbeschreibung",
        author="Meeting Manager",
    )
    story = _markdown_story(source.read_text(encoding="utf-8"))
    document.build(story)
    response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="Meeting_Manager_Funktions-und-Sicherheitsbeschreibung.pdf"'
    response["Cache-Control"] = "private, no-store"
    response["X-Content-Type-Options"] = "nosniff"
    return response
