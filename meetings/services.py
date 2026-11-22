from datetime import timedelta
from django.utils import timezone
from .models import Meeting, AgendaItem, Topic, TopicSnapshot

def ensure_agenda(meeting):
    """Return explicit agenda items and carry forward unresolved items once."""
    if meeting.series_id is None:
        return meeting.agenda_items.select_related("topic", "assigned_to", "topic__assigned_to").all()

    previous = (
        Meeting.objects.filter(series=meeting.series, date__lt=meeting.date, finalized_at__isnull=False)
        .order_by("-date").first()
    )
    if previous:
        carried = previous.agenda_items.filter(
            topic__status__in=["open", "in_progress"],
            topic__series=meeting.series,
        ).exclude(
            topic__agenda_items__meeting__date__gt=previous.date,
            topic__agenda_items__meeting__date__lt=meeting.date,
        ).select_related("topic")
        for item in carried:
            AgendaItem.objects.get_or_create(
                meeting=meeting,
                topic=item.topic,
                defaults={
                    "working_text": item.working_text,
                    "carried_forward": True,
                },
            )
    return meeting.agenda_items.select_related("topic", "assigned_to", "topic__assigned_to").all()

def _next_weekday_on_or_after(day, weekday):
    return day + timedelta(days=(weekday - day.weekday()) % 7)


def _monthly_weekday(year, month, weekday, occurrence):
    import calendar
    from datetime import date
    first_weekday, days_in_month = calendar.monthrange(year, month)
    first_day = 1 + (weekday - first_weekday) % 7
    day = first_day + (occurrence - 1) * 7
    if day > days_in_month:
        day -= 7
    return date(year, month, day)


def generate_meetings(series):
    from datetime import date
    created = []
    today = timezone.localdate()
    end_date = series.end_date or date(today.year + 1, 12, 31)
    if series.end_date is None:
        series.end_date = end_date
        series.save(update_fields=["end_date"])
    cursor = _next_weekday_on_or_after(series.start_date, series.weekday)
    interval = max(1, series.recurrence_interval or 1)
    occurrence = (cursor.day - 1) // 7 + 1
    while cursor <= end_date:
        if cursor >= today:
            meeting, made = Meeting.objects.get_or_create(series=series, date=cursor)
            if made:
                created.append(meeting)
        if series.recurrence in ("weekly", "biweekly"):
            weeks = interval * (2 if series.recurrence == "biweekly" else 1)
            cursor += timedelta(days=7 * weeks)
        else:
            month_index = cursor.year * 12 + cursor.month - 1 + interval
            year, month_zero = divmod(month_index, 12)
            cursor = _monthly_weekday(year, month_zero + 1, series.weekday, occurrence)
    return created

def finalize_meeting(meeting):
    if meeting.finalized_at: return
    ensure_agenda(meeting)
    for item in meeting.agenda_items.select_related("topic"):
        topic = item.topic
        TopicSnapshot.objects.get_or_create(meeting=meeting, topic_id=topic.pk, defaults={
            "topic_title": topic.title, "text": item.working_text, "status": topic.status
        })
        topic.description = item.working_text
        topic.save(update_fields=["description","updated_at"])
    meeting.finalized_at = timezone.now()
    meeting.save(update_fields=["finalized_at"])
