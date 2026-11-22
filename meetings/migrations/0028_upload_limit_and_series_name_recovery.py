from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import migrations, models


def restore_unambiguous_series_names(apps, schema_editor):
    Meeting = apps.get_model("meetings", "Meeting")
    AuditEvent = apps.get_model("meetings", "AuditEvent")
    db = schema_editor.connection.alias
    for meeting in Meeting.objects.using(db).filter(series__isnull=True, archived_series_name="").iterator():
        names = set()
        for event in AuditEvent.objects.using(db).filter(meeting_id=meeting.pk).only("changes"):
            entry = (event.changes or {}).get("Besprechungsreihe")
            if isinstance(entry, dict):
                previous = (entry.get("vorher") or "").strip()
                if previous:
                    names.add(previous)
        if len(names) == 1:
            meeting.archived_series_name = names.pop()[:160]
            meeting.save(update_fields=["archived_series_name"], using=db)


class Migration(migrations.Migration):
    dependencies = [("meetings", "0027_meeting_archived_series_name")]
    operations = [
        migrations.AddField(
            model_name="organizationsettings",
            name="attachment_max_size_mb",
            field=models.PositiveSmallIntegerField(
                default=20,
                help_text="Gilt für hochgeladene Themenanlagen. Zulässig sind 1 bis 25 MB.",
                validators=[MinValueValidator(1), MaxValueValidator(25)],
                verbose_name="Maximale Dateigröße für Anlagen (MB)",
            ),
        ),
        migrations.RunPython(restore_unambiguous_series_names, migrations.RunPython.noop),
    ]
