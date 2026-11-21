from django.db import migrations, models
import django.db.models.deletion


def backfill_audit_event_series(apps, schema_editor):
    AuditEvent = apps.get_model("meetings", "AuditEvent")
    db_alias = schema_editor.connection.alias
    for event in AuditEvent.objects.using(db_alias).select_related("meeting", "topic").iterator():
        series_id = None
        if event.meeting_id:
            series_id = event.meeting.series_id
        if not series_id and event.topic_id:
            series_id = event.topic.series_id
        if series_id:
            AuditEvent.objects.using(db_alias).filter(pk=event.pk).update(series_id=series_id)


class Migration(migrations.Migration):

    dependencies = [
        ("meetings", "0012_topic_in_progress_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="auditevent",
            name="series",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="audit_events",
                to="meetings.meetingseries",
            ),
        ),
        migrations.RunPython(backfill_audit_event_series, migrations.RunPython.noop),
    ]
