"""Permission-scoped CSV export for the audit history."""
import csv
import json
from io import StringIO

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse, HttpResponseForbidden

from .access import is_admin, is_auditor
from .models import AuditEvent, MeetingSeries, SeriesAccess, Topic
from .user_display import user_display_name


def _safe_csv_cell(value):
    """Prevent spreadsheet formula execution from user-controlled audit data."""
    text = str(value or "")
    if text.lstrip(" \t\r\n")[:1] in ("=", "+", "-", "@"):
        return "'" + text
    return text


@login_required
def audit_history_csv(request):
    admin_access = is_admin(request.user) or is_auditor(request.user)
    series = (MeetingSeries.objects.none() if admin_access else MeetingSeries.objects.filter(
        user_access__user=request.user,
        user_access__role=SeriesAccess.ROLE_MODERATOR,
    ).distinct())
    if not admin_access and not series.exists():
        return HttpResponseForbidden("Für deinen Zugang ist der Export des Änderungsverlaufs nicht freigegeben.")

    events = AuditEvent.objects.select_related("actor", "topic", "meeting", "meeting__series", "series")
    if admin_access:
        events = events.filter(scope=AuditEvent.SCOPE_SYSTEM)
    else:
        events = events.filter(
            Q(series__in=series)
            | (Q(series__isnull=True) & (
                Q(topic__series__in=series)
                | (Q(topic__series__isnull=True) & Q(meeting__series__in=series))
            ))
        )
    topics = Topic.objects.none() if admin_access else Topic.objects.filter(series__in=series)
    selected_series = request.GET.get("series", "")
    if selected_series.isdigit() and series.filter(pk=int(selected_series)).exists():
        series_id = int(selected_series)
        events = events.filter(Q(series_id=series_id) | (Q(series__isnull=True) & (Q(topic__series_id=series_id) | Q(meeting__series_id=series_id))))
        topics = topics.filter(series_id=series_id)
    selected_action = request.GET.get("action", "")
    if selected_action in {value for value, label in AuditEvent.ACTIONS}:
        events = events.filter(action=selected_action)
    topic_id = request.GET.get("topic", "")
    if topic_id and topics.filter(pk=topic_id).exists():
        events = events.filter(topic_id=topic_id)
    output = StringIO()
    writer = csv.writer(output, delimiter=";", lineterminator="\r\n")
    writer.writerow(["Zeitpunkt", "Aktion", "Benutzer", "Besprechungsreihe", "Thema", "Besprechung", "Beschreibung", "Änderungsdetails"])
    for event in events.order_by("-created_at", "-pk").iterator():
        series_name = event.series.name if event.series_id else (
            event.meeting.series.name if event.meeting_id and event.meeting.series_id else
            event.topic.series.name if event.topic_id and event.topic.series_id else (event.meeting.archived_series_name if event.meeting_id else "")
        )
        meeting_label = ""
        if event.meeting_id:
            meeting_label = f"{event.meeting.date.isoformat()} – {event.meeting.title or 'Besprechung'}"
        writer.writerow([
            event.created_at.isoformat(),
            event.get_action_display(),
            _safe_csv_cell(
                user_display_name(event.actor)
                if event.actor_id else "System / gelöschter Benutzer"
            ),
            _safe_csv_cell(series_name),
            _safe_csv_cell(event.topic.title if event.topic_id else ""),
            _safe_csv_cell(meeting_label),
            _safe_csv_cell(event.summary),
            _safe_csv_cell(json.dumps(event.changes, ensure_ascii=False, sort_keys=True)),
        ])
    response = HttpResponse("\ufeff" + output.getvalue(), content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="aenderungsverlauf.csv"'
    return response
