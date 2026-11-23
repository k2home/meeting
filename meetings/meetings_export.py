"""CSV export of the current user's accessible meeting schedule."""
import csv
from io import StringIO

from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.http import HttpResponse

from .access import accessible_meetings, is_admin
from .models import SeriesAccess


@login_required
def meetings_csv(request):
    meetings = (accessible_meetings(request.user).filter(series__isnull=False)
                .select_related("series")
                .annotate(open_agenda_count=Count(
                    "agenda_items", filter=Q(agenda_items__status__in=["open", "in_progress"])
                )).order_by("date", "series__name", "pk"))
    role_by_series = {}
    if not is_admin(request.user):
        role_by_series = {
            access.series_id: access.get_role_display()
            for access in SeriesAccess.objects.filter(user=request.user)
        }

    output = StringIO()
    writer = csv.writer(output, delimiter=";", lineterminator="\r\n")
    writer.writerow(["Datum", "Besprechungsreihe", "Besprechung", "Eigene Rolle", "Status", "Offene Tagesordnungspunkte"])
    for meeting in meetings:
        writer.writerow([
            meeting.date.isoformat(), meeting.series.name, meeting.title or "Besprechung",
            "Administrator" if is_admin(request.user) else role_by_series.get(meeting.series_id, ""),
            "Abgeschlossen" if meeting.finalized_at else "Offen",
            meeting.open_agenda_count,
        ])
    response = HttpResponse("\ufeff" + output.getvalue(), content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="besprechungen.csv"'
    return response
