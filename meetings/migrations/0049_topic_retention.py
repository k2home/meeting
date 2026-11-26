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
        reopened_event = AuditEvent.objects.using(db).filter(
            topic_id=topic.pk, action="reopened"
        ).order_by("-created_at", "-pk").first()
        if archived_event and (
            not reopened_event or archived_event.created_at > reopened_event.created_at
        ):
            archived_at = archived_event.created_at.date()
        else:
            # Some legacy archive paths (such as deleting a series or CSV import)
            # did not create a topic-specific archive event. Use migration time
            # rather than risk deleting those topics earlier than intended.
            archived_at = timezone.now().date()
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
