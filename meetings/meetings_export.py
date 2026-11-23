"""CSV export of the current user's accessible meeting schedule."""
import csv
from io import StringIO

from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.http import HttpResponse

from .access import accessible_meetings, is_admin
from .models import ArchivedMeetingAccess, SeriesAccess


def _safe_csv_cell(value):
    """Prevent spreadsheet formula execution from user-controlled CSV values."""
    text = str(value or "")
    if text.lstrip(" \\t\\r\\n")[:1] in ("=", "+", "-", "@"):
        return "'" + text
    return text


@login_required
def meetings_csv(request):
    meetings = (accessible_meetings(request.user)
                .select_related("series")
                .annotate(open_agenda_count=Count(
                    "agenda_items", filter=Q(agenda_items__status__in=["open", "in_progress"])
                )).order_by("date", "series__name", "pk"))
    admin_access = is_admin(request.user)
    role_by_series = {}
    archived_role_by_meeting = {}
    if not admin_access:
        role_by_series = {
            access.series_id: access.get_role_display()
            for access in SeriesAccess.objects.filter(user=request.user)
        }
        archived_role_labels = dict(SeriesAccess.ROLE_CHOICES)
        archived_role_by_meeting = {
            meeting_id: archived_role_labels.get(role, "Archivzugriff")
            for meeting_id, role in ArchivedMeetingAccess.objects.filter(
                user=request.user
            ).values_list("meeting_id", "role")
        }

    output = StringIO()
    writer = csv.writer(output, delimiter=";", lineterminator="\r\n")
    writer.writerow(["Datum", "Besprechungsreihe", "Besprechung", "Eigene Rolle", "Status", "Offene Tagesordnungspunkte"])
    for meeting in meetings:
        writer.writerow([
            meeting.date.isoformat(),
            _safe_csv_cell(
                meeting.series.name if meeting.series_id
                else meeting.archived_series_name or "Gelöschte Besprechungsreihe"
            ),
            _safe_csv_cell(meeting.title or "Besprechung"),
            "Administrator" if admin_access else (
                role_by_series.get(meeting.series_id, "")
                if meeting.series_id else archived_role_by_meeting.get(meeting.pk, "Archivzugriff")
            ),
            "Abgeschlossen" if meeting.finalized_at else "Offen",
            meeting.open_agenda_count,
        ])
    response = HttpResponse("\ufeff" + output.getvalue(), content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="besprechungen.csv"'
    return response
