from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import migrations, models
import django.db.models.deletion


def normalize_series_values(apps, schema_editor):
    MeetingSeries = apps.get_model("meetings", "MeetingSeries")
    alias = schema_editor.connection.alias
    MeetingSeries.objects.using(alias).filter(recurrence_interval__lt=1).update(recurrence_interval=1)
    MeetingSeries.objects.using(alias).filter(recurrence_interval__gt=52).update(recurrence_interval=52)
    MeetingSeries.objects.using(alias).filter(end_date__lt=models.F("start_date")).update(end_date=models.F("start_date"))


class Migration(migrations.Migration):
    dependencies = [
        ("meetings", "0024_validate_meeting_series_weekday"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RunPython(normalize_series_values, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="meetingseries",
            name="recurrence_interval",
            field=models.PositiveSmallIntegerField(
                default=1,
                validators=[MinValueValidator(1), MaxValueValidator(52)],
                verbose_name="Wiederholungsintervall",
            ),
        ),
        migrations.AddConstraint(
            model_name="meetingseries",
            constraint=models.CheckConstraint(
                condition=models.Q(recurrence_interval__gte=1, recurrence_interval__lte=52),
                name="meeting_series_interval_1_52",
            ),
        ),
        migrations.AddConstraint(
            model_name="meetingseries",
            constraint=models.CheckConstraint(
                condition=models.Q(end_date__isnull=True) | models.Q(end_date__gte=models.F("start_date")),
                name="meeting_series_end_after_start",
            ),
        ),
        migrations.CreateModel(
            name="ArchivedMeetingAccess",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("role", models.CharField(blank=True, max_length=16, verbose_name="Ehemalige Rolle")),
                ("meeting", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="archived_access", to="meetings.meeting")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="archived_meeting_access", to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddConstraint(
            model_name="archivedmeetingaccess",
            constraint=models.UniqueConstraint(fields=("meeting", "user"), name="unique_archived_meeting_user"),
        ),
    ]
