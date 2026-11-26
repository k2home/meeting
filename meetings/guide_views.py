from io import BytesIO
from pathlib import Path
import re
from xml.sax.saxutils import escape

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
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
                '<input type="checkbox" class="test-checklist-box" '
                f'data-checklist-line="{line_number}" '
                f'data-checklist-occurrence="{occurrence}"'
                f'{checked_attribute}{disabled_attribute}>'
            )

        rendered_lines.append(re.sub(r"\[([ xX])\]", render_checkbox, line))
    return "".join(rendered_lines)


@login_required
def test_documentation(request):
    """Render the manual test checklist; editing and Markdown export are TESTING-only."""
    source = Path(settings.BASE_DIR) / "docs" / "Pruefung-des-Verfahrens-Testdokumentation.md"
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
        "test_documentation_markdown": markdown_source,
        "test_documentation_editable": testing_mode,
    })


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
