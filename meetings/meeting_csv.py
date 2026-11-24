import csv
import io

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.text import slugify

from .access import accessible_meetings
from .user_display import user_display_name


def _spreadsheet_safe(value):
    value = "" if value is None else str(value)
    if value.lstrip(" \t\r\n").startswith(("=", "+", "-", "@")):
        return "'" + value
    return value


@login_required
def meeting_participants_csv(request, pk):
    """Export participants only when the current user may access the meeting."""
    meeting = get_object_or_404(
        accessible_meetings(request.user).select_related("series"),
        pk=pk,
    )
    participants = meeting.participants.filter(is_active=True).order_by(
        "last_name", "first_name", "username"
    )

    output = io.StringIO(newline="")
    writer = csv.writer(output, delimiter=";", lineterminator="\r\n")
    writer.writerow(["Teilnehmer"])
    for participant in participants:
        writer.writerow([
            _spreadsheet_safe(user_display_name(participant, include_short_description=False)),
        ])

    series_name = meeting.series.name if meeting.series_id else meeting.archived_series_name
    filename = slugify(series_name or "besprechung") or "besprechung"
    response = HttpResponse("\ufeff" + output.getvalue(), content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = (
        f'attachment; filename="teilnehmer-{filename}-{meeting.date:%Y-%m-%d}.csv"'
    )
    return response
