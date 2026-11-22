from datetime import timedelta
from django.utils import timezone
from .models import Meeting, AgendaItem, Topic, TopicSnapshot

def ensure_agenda(meeting):
    if meeting.series_id is None:
        return meeting.agenda_items.select_related("topic").all()
    due = Topic.objects.filter(series=meeting.series, status="open", due_date__lte=meeting.date)
    previous = Meeting.objects.filter(series=meeting.series, date__lt=meeting.date, finalized_at__isnull=False).order_by("-date").first()
    carried_ids = []
    if previous:
        carried_ids = list(previous.agenda_items.filter(topic__status="open", topic__series=meeting.series).values_list("topic_id", flat=True))
    candidates = (due | Topic.objects.filter(id__in=carried_ids)).distinct()
    for topic in candidates:
        AgendaItem.objects.get_or_create(meeting=meeting, topic=topic, defaults={"working_text": "", "carried_forward": topic.id in carried_ids})
    return meeting.agenda_items.select_related("topic").all()

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
    created = []
    today = timezone.localdate()
    cursor = _next_weekday_on_or_after(series.start_date, series.weekday)
    interval = max(1, series.recurrence_interval or 1)
    occurrence = (cursor.day - 1) // 7 + 1
    while not series.end_date or cursor <= series.end_date:
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
