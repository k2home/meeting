"""CSV export of the signed-in user's personal task list."""
import csv
from io import StringIO

from django.contrib.auth.decorators import login_required
from django.db.models import Min, Q
from django.http import HttpResponse
from django.utils import timezone

from .access import accessible_meetings, accessible_topics
from .models import AgendaItem


@login_required
def personal_tasks_csv(request):
    today = timezone.localdate()
    visible_meetings = accessible_meetings(request.user)
    topics = (accessible_topics(request.user)
              .filter(assigned_to=request.user, status__in=["open", "in_progress"])
              .select_related("series")
              .annotate(next_meeting_date=Min(
                  "agenda_items__meeting__date",
                  filter=Q(agenda_items__meeting__in=visible_meetings)
                  & Q(agenda_items__meeting__finalized_at__isnull=True),
              )).distinct().order_by("title"))
    agenda_items = (AgendaItem.objects.filter(
        meeting__in=visible_meetings, meeting__date__gte=today,
        meeting__finalized_at__isnull=True, assigned_to=request.user,
        status__in=["open", "in_progress"],
    ).select_related("topic", "topic__series", "meeting")
      .order_by("meeting__date", "meeting__series__name", "position", "pk"))

    output = StringIO()
    writer = csv.writer(output, delimiter=";", lineterminator="\r\n")
    writer.writerow(["Aufgabentyp", "Thema", "Besprechungsreihe", "Nächster Termin", "Status", "Protokolltext"])
    for topic in topics:
        writer.writerow([
            "Hauptzuständigkeit", topic.title, topic.series.name if topic.series else "",
            topic.next_meeting_date.isoformat() if topic.next_meeting_date else "",
            topic.get_status_display(), "",
        ])
    for item in agenda_items:
        writer.writerow([
            "Tagesordnungspunkt", item.topic.title,
            item.topic.series.name if item.topic.series else item.meeting.series.name if item.meeting.series else "",
            item.meeting.date.isoformat(), item.get_status_display(), item.working_text,
        ])
    response = HttpResponse("\ufeff" + output.getvalue(), content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="meine-aufgaben.csv"'
    return response
