"""iCalendar export for meetings visible to the signed-in user."""
from datetime import datetime, timedelta, timezone as datetime_timezone

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from .access import accessible_meetings


def _escape_ical_text(value):
    """Escape text according to RFC 5545 section 3.3.11."""
    return (str(value or "").replace("\\", "\\\\")
            .replace(";", "\\;").replace(",", "\\,")
            .replace("\r\n", "\\n").replace("\n", "\\n").replace("\r", "\\n"))


def _fold_ical_line(line):
    """Fold UTF-8 content lines at 75 octets without splitting characters."""
    parts, current, size = [], "", 0
    for character in line:
        char_size = len(character.encode("utf-8"))
        if size + char_size > 75:
            parts.append(current)
            current, size = " ", 1
        current += character
        size += char_size
    parts.append(current)
    return "\r\n".join(parts)


@login_required
def calendar_export(request):
    """Download all meetings from series the current user may access."""
    meetings = (accessible_meetings(request.user).filter(series__isnull=False)
                .select_related("series").order_by("date", "series__name", "pk"))
    stamp = datetime.now(datetime_timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0",
             "PRODID:-//Meeting Manager//Meeting Calendar//DE", "CALSCALE:GREGORIAN",
             "METHOD:PUBLISH"]
    for meeting in meetings:
        end_date = meeting.date + timedelta(days=1)
        lines.extend(["BEGIN:VEVENT", f"UID:meeting-{meeting.pk}@meeting-manager",
                      f"DTSTAMP:{stamp}", f"DTSTART;VALUE=DATE:{meeting.date:%Y%m%d}",
                      f"DTEND;VALUE=DATE:{end_date:%Y%m%d}",
                      f"SUMMARY:{_escape_ical_text(meeting.title or 'Besprechung')}",
                      f"DESCRIPTION:{_escape_ical_text(meeting.series.name)}", "END:VEVENT"])
    lines.append("END:VCALENDAR")
    payload = "\r\n".join(_fold_ical_line(line) for line in lines) + "\r\n"
    response = HttpResponse(payload, content_type="text/calendar; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="meeting-manager.ics"'
    return response
