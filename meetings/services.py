from datetime import timedelta
from django.utils import timezone
from django.db import transaction
from .models import Meeting, AgendaItem, Topic, TopicSnapshot
from .user_display import user_display_name

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
            status__in=["open", "in_progress"],
            topic__series=meeting.series,
        ).exclude(
            topic__agenda_items__meeting__date__gt=previous.date,
        ).select_related("topic")
        for item in carried:
            AgendaItem.objects.get_or_create(
                meeting=meeting,
                topic=item.topic,
                defaults={
                    "working_text": item.working_text,
                    "carried_forward": True,
                    "assigned_to_id": item.assigned_to_id,
                    "status": item.status,
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


@transaction.atomic
def generate_meetings(series):
    """Reconcile future draft meetings and move agenda items to the nearest new date."""
    from datetime import date

    today = timezone.localdate()
    end_date = series.end_date or date(today.year + 1, 12, 31)
    if series.end_date is None:
        series.end_date = end_date
        series.save(update_fields=["end_date"])

    cursor = _next_weekday_on_or_after(series.start_date, series.weekday)
    interval = max(1, series.recurrence_interval or 1)
    occurrence = (cursor.day - 1) // 7 + 1
    desired_dates = []
    while cursor <= end_date:
        if cursor >= today:
            desired_dates.append(cursor)
        if series.recurrence in ("weekly", "biweekly"):
            cursor += timedelta(days=7 * interval * (2 if series.recurrence == "biweekly" else 1))
        else:
            month_index = cursor.year * 12 + cursor.month - 1 + interval
            year, month_zero = divmod(month_index, 12)
            cursor = _monthly_weekday(year, month_zero + 1, series.weekday, occurrence)

    obsolete_qs = Meeting.objects.filter(series=series, date__gte=today, finalized_at__isnull=True)
    if not desired_dates:
        if obsolete_qs.filter(agenda_items__isnull=False).exists():
            raise ValueError("Der neue Terminplan enthält keinen zukünftigen Termin, auf den vorhandene Tagesordnungspunkte übertragen werden können. Bitte passe Start- oder Enddatum an.")
        obsolete_qs.delete()
        return []

    desired_meetings, created = {}, []
    for meeting_date in desired_dates:
        meeting, made = Meeting.objects.get_or_create(series=series, date=meeting_date)
        desired_meetings[meeting_date] = meeting
        if made:
            created.append(meeting)

    status_rank = {"open": 0, "in_progress": 1, "done": 2}
    obsolete = list(obsolete_qs.exclude(date__in=desired_dates).order_by("date", "pk"))
    for old_meeting in obsolete:
        target_date = min(desired_dates, key=lambda d: (abs((d - old_meeting.date).days), d))
        target = desired_meetings[target_date]
        if old_meeting.participants.exists():
            target.participants.add(*old_meeting.participants.all())
        if old_meeting.title and not target.title:
            target.title = old_meeting.title
            target.save(update_fields=["title"])
        for item in old_meeting.agenda_items.select_related("topic").order_by("position", "pk"):
            existing = target.agenda_items.filter(topic_id=item.topic_id).first()
            if existing:
                existing.working_text = "\n\n".join(dict.fromkeys(
                    value for value in (existing.working_text, item.working_text) if value
                ))
                if not existing.assigned_to_id and item.assigned_to_id:
                    existing.assigned_to_id = item.assigned_to_id
                if status_rank.get(item.status, 0) > status_rank.get(existing.status, 0):
                    existing.status = item.status
                existing.carried_forward = True
                existing.save(update_fields=["working_text", "assigned_to", "status", "carried_forward"])
                item.delete()
            else:
                item.meeting = target
                item.position = (target.agenda_items.order_by("-position").values_list("position", flat=True).first() if target.agenda_items.exists() else -1) + 1
                item.carried_forward = True
                item.save(update_fields=["meeting", "position", "carried_forward"])
        old_meeting.delete()
    return created

def finalize_meeting(meeting):
    if meeting.finalized_at: return
    ensure_agenda(meeting)
    for item in meeting.agenda_items.select_related("topic"):
        topic = item.topic
        TopicSnapshot.objects.get_or_create(meeting=meeting, topic_id=topic.pk, defaults={
            "topic_title": topic.title, "text": item.working_text, "status": item.status,
            "responsible_name": user_display_name(item.assigned_to) if item.assigned_to else ""
        })
    meeting.finalized_at = timezone.now()
    meeting.save(update_fields=["finalized_at"])
