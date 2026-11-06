from .models import AuditEvent


def record_event(*, actor, action, summary, topic=None, meeting=None, changes=None):
    """Write one append-only audit entry. Never store passwords or uploaded file contents."""
    return AuditEvent.objects.create(
        actor=actor if getattr(actor, "is_authenticated", False) else None,
        action=action,
        summary=summary[:500],
        topic=topic,
        meeting=meeting,
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
