from datetime import timedelta
from django.utils import timezone
from .models import Meeting, AgendaItem, Topic, TopicSnapshot

def ensure_agenda(meeting):
    due = Topic.objects.filter(series=meeting.series, status="open", due_date__lte=meeting.date)
    previous = Meeting.objects.filter(series=meeting.series, date__lt=meeting.date, finalized_at__isnull=False).order_by("-date").first()
    carried_ids = []
    if previous:
        carried_ids = list(previous.agenda_items.filter(topic__status="open").values_list("topic_id", flat=True))
    candidates = (due | Topic.objects.filter(id__in=carried_ids)).distinct()
    for topic in candidates:
        AgendaItem.objects.get_or_create(meeting=meeting, topic=topic, defaults={"working_text": topic.description, "carried_forward": topic.id in carried_ids})
    return meeting.agenda_items.select_related("topic").all()

def generate_meetings(series, count=24):
    cursor = series.start_date
    today = timezone.localdate()
    created = []
    for _ in range(count):
        if series.end_date and cursor > series.end_date: break
        if cursor >= today:
            obj, made = Meeting.objects.get_or_create(series=series, date=cursor)
            if made: created.append(obj)
        if series.recurrence == "weekly": cursor += timedelta(days=7)
        elif series.recurrence == "biweekly": cursor += timedelta(days=14)
        else:
            import calendar
            year, month = cursor.year, cursor.month + 1
            if month == 13: year, month = year + 1, 1
            cursor = cursor.replace(year=year, month=month, day=min(cursor.day, calendar.monthrange(year, month)[1]))
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
