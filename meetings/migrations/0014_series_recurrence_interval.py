from django.db import migrations, models


def migrate_biweekly_recurrence(apps, schema_editor):
    MeetingSeries = apps.get_model("meetings", "MeetingSeries")
    MeetingSeries.objects.using(schema_editor.connection.alias).filter(
        recurrence="biweekly"
    ).update(recurrence="weekly", recurrence_interval=2)


class Migration(migrations.Migration):

    dependencies = [
        ("meetings", "0013_audit_event_series"),
    ]

    operations = [
        migrations.AddField(
            model_name="meetingseries",
            name="recurrence_interval",
            field=models.PositiveSmallIntegerField(default=1, verbose_name="Wiederholungsintervall"),
        ),
        migrations.RunPython(migrate_biweekly_recurrence, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="meetingseries",
            name="recurrence",
            field=models.CharField(
                choices=[("weekly", "Wöchentlich"), ("monthly", "Monatlich")],
                default="monthly",
                max_length=12,
                verbose_name="Wiederholung",
            ),
        ),
    ]
