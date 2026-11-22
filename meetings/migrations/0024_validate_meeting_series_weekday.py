from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import migrations, models


def normalize_invalid_weekdays(apps, schema_editor):
    MeetingSeries = apps.get_model("meetings", "MeetingSeries")
    MeetingSeries.objects.using(schema_editor.connection.alias).filter(
        weekday__gt=6
    ).update(weekday=0)


class Migration(migrations.Migration):

    dependencies = [
        ("meetings", "0023_alter_auditevent_action"),
    ]

    operations = [
        migrations.RunPython(normalize_invalid_weekdays, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="meetingseries",
            name="weekday",
            field=models.PositiveSmallIntegerField(
                default=0,
                validators=[MinValueValidator(0), MaxValueValidator(6)],
                verbose_name="Wochentag (0=Mo)",
            ),
        ),
        migrations.AddConstraint(
            model_name="meetingseries",
            constraint=models.CheckConstraint(
                condition=models.Q(("weekday__gte", 0), ("weekday__lte", 6)),
                name="meeting_series_weekday_0_6",
            ),
        ),
    ]
