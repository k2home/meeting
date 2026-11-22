from django.db import migrations


DESCRIPTION_KEYS = {
    "description",
    "beschreibung",
    "aktueller stand",
    "bisherige themenbeschreibung",
    "topic_current_status",
}


def _without_topic_description(value):
    if isinstance(value, dict):
        return {
            key: _without_topic_description(item)
            for key, item in value.items()
            if str(key).strip().casefold() not in DESCRIPTION_KEYS
        }
    if isinstance(value, list):
        return [_without_topic_description(item) for item in value]
    return value


def remove_topic_description_from_audit(apps, schema_editor):
    AuditEvent = apps.get_model("meetings", "AuditEvent")
    database = schema_editor.connection.alias
    events = AuditEvent.objects.using(database).filter(topic__isnull=False).only("pk", "changes")
    for event in events.iterator():
        cleaned = _without_topic_description(event.changes or {})
        if cleaned != (event.changes or {}):
            AuditEvent.objects.using(database).filter(pk=event.pk).update(changes=cleaned)


class Migration(migrations.Migration):
    dependencies = [("meetings", "0019_agendaitem_status")]

    operations = [
        migrations.RunPython(remove_topic_description_from_audit, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name="topic",
            name="description",
        ),
    ]
