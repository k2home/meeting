from django.db import migrations, models
from django.core.validators import MinValueValidator
from django.utils import timezone


def backfill_archived_dates(apps, schema_editor):
    Topic = apps.get_model("meetings", "Topic")
    AuditEvent = apps.get_model("meetings", "AuditEvent")
    db = schema_editor.connection.alias
    for topic in Topic.objects.using(db).filter(status="archived", archived_at__isnull=True).iterator():
        archived_event = AuditEvent.objects.using(db).filter(
            topic_id=topic.pk, action="archived"
        ).order_by("-created_at", "-pk").first()
        archived_at = archived_event.created_at.date() if archived_event else timezone.now().date()
        Topic.objects.using(db).filter(pk=topic.pk).update(archived_at=archived_at)


class Migration(migrations.Migration):
    dependencies = [("meetings", "0048_auditevent_scope")]

    operations = [
        migrations.AddField(
            model_name="organizationsettings",
            name="retention_years",
            field=models.PositiveSmallIntegerField(
                default=10,
                validators=[MinValueValidator(1)],
                verbose_name="Aufbewahrungsfrist für Themen und Protokolle (Jahre)",
                help_text="Gilt als Standard für archivierte Themen und abgeschlossene Protokollstände. Eine abweichende Frist kann im jeweiligen Thema festgelegt werden.",
            ),
        ),
        migrations.AddField(
            model_name="topic",
            name="archived_at",
            field=models.DateField(blank=True, null=True, verbose_name="Archiviert am"),
        ),
        migrations.AddField(
            model_name="topic",
            name="retention_years",
            field=models.PositiveSmallIntegerField(
                blank=True, null=True,
                validators=[MinValueValidator(1)],
                verbose_name="Löschfrist (Jahre)",
            ),
        ),
        migrations.RunPython(backfill_archived_dates, migrations.RunPython.noop),
    ]
