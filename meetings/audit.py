import json
import logging

from .models import AuditEvent


security_audit_logger = logging.getLogger("meetings.security_audit")


def record_event(*, actor, action, summary, topic=None, meeting=None, series=None, changes=None):
    """Persist an audit entry and emit a metadata-only event for external log forwarding."""
    event = AuditEvent.objects.create(
        actor=actor if getattr(actor, "is_authenticated", False) else None,
        action=action,
        summary=summary[:500],
        topic=topic,
        meeting=meeting,
        series=(series or (meeting.series if meeting is not None and meeting.series_id else (topic.series if topic is not None else None))),
        changes=changes or {},
    )
    # Do not duplicate free text, before/after values, filenames or file contents
    # into infrastructure logs. The event ID links the external record to the DB row.
    security_audit_logger.info(json.dumps({
        "event": "meeting_manager.audit",
        "audit_id": event.pk,
        "timestamp": event.created_at.isoformat(),
        "scope": event.scope,
        "actor_id": event.actor_id,
        "action": event.action,
        "series_id": event.series_id,
        "meeting_id": event.meeting_id,
        "topic_id": event.topic_id,
    }, separators=(",", ":"), ensure_ascii=True))
    return event


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
