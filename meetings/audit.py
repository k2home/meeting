from .models import AuditEvent


def record_event(*, actor, action, summary, topic=None, meeting=None, series=None, changes=None):
    """Write one append-only audit entry. Never store passwords or uploaded file contents."""
    return AuditEvent.objects.create(
        actor=actor if getattr(actor, "is_authenticated", False) else None,
        action=action,
        summary=summary[:500],
        topic=topic,
        meeting=meeting,
        series=(series or (meeting.series if meeting is not None and meeting.series_id else (topic.series if topic is not None else None))),
        changes=changes or {},
    )


def changed_fields(before, after, fields):
    """Build a JSON-safe before/after map for the fields that actually changed."""
    result = {}
    for field, label in fields.items():
        old = before.get(field)
        new = after.get(field)
        if old != new:
            result[label] = {"vorher": old, "nachher": new}
    return result


def record_transfer_events(*, actor, summary, topic, from_series, to_series, meeting=None, changes=None):
    """Make a transfer visible in both the source and destination series histories."""
    payload = dict(
        actor=actor, action="transferred", summary=summary, topic=topic,
        meeting=meeting, changes=changes or {},
    )
    if from_series is not None:
        record_event(**payload, series=from_series)
    if to_series is not None and (from_series is None or to_series.pk != from_series.pk):
        record_event(**payload, series=to_series)
