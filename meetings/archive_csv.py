import csv
import io

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils.text import slugify

from .access import accessible_meetings, accessible_series, accessible_topics
from .models import AgendaItem


def _safe_csv_value(value):
    value = "" if value is None else str(value)
    if value.lstrip(" \t\r\n").startswith(("=", "+", "-", "@")):
        return "'" + value
    return value


@login_required
def archive_csv_export(request):
    """Export the current user's accessible archived topics and completed agenda items."""
    series = accessible_series(request.user).distinct()
    selected_series = request.GET.get("series", "").strip()
    series_id = (
        int(selected_series)
        if selected_series.isdigit() and series.filter(pk=int(selected_series)).exists()
        else None
    )

    archived_topics = accessible_topics(request.user).filter(
        status="archived"
    ).select_related("series", "assigned_to").order_by("series__name", "title")
    completed_items = AgendaItem.objects.filter(
        meeting__in=accessible_meetings(request.user), status="done"
    ).select_related(
        "topic", "topic__series", "topic__assigned_to",
        "meeting", "meeting__series", "assigned_to",
    ).order_by("-meeting__date", "topic__title", "position")

    if series_id is not None:
        archived_topics = archived_topics.filter(series_id=series_id)
        completed_items = completed_items.filter(meeting__series_id=series_id)

    output = io.StringIO(newline="")
    writer = csv.writer(output, delimiter=";", lineterminator="\r\n")
    writer.writerow([
        "Typ", "Thema", "Besprechungsreihe", "Termin",
        "Status", "Verantwortlich", "Text",
    ])

    for topic in archived_topics:
        writer.writerow([
            _safe_csv_value("Archiviertes Thema"),
            _safe_csv_value(topic.title),
            _safe_csv_value(topic.series.name if topic.series_id else "Ohne Besprechungsreihe"),
            "",
            _safe_csv_value(topic.get_status_display()),
            _safe_csv_value(topic.assigned_to.get_full_name() or topic.assigned_to.username if topic.assigned_to else ""),
            "",
        ])

    for item in completed_items:
        series_name = (
            item.meeting.series.name if item.meeting.series_id
            else item.meeting.archived_series_name or "Ohne Besprechungsreihe"
        )
        responsible = item.assigned_to or item.topic.assigned_to
        responsible_name = (
            responsible.get_full_name() or responsible.username if responsible else ""
        )
        writer.writerow([
            _safe_csv_value("Erledigter Tagesordnungspunkt"),
            _safe_csv_value(item.topic.title),
            _safe_csv_value(series_name),
            item.meeting.date.isoformat(),
            _safe_csv_value(item.get_status_display()),
            _safe_csv_value(responsible_name),
            _safe_csv_value(item.working_text),
        ])

    response = HttpResponse("\ufeff" + output.getvalue(), content_type="text/csv; charset=utf-8")
    filename = "archiv"
    if series_id is not None:
        series_name = series.filter(pk=series_id).values_list("name", flat=True).first()
        filename += "-" + (slugify(series_name or "") or str(series_id))
    response["Content-Disposition"] = f'attachment; filename="{filename}.csv"'
    return response
