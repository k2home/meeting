from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def move_topic_due_dates_to_agenda(apps, schema_editor):
    Topic = apps.get_model("meetings", "Topic")
    Meeting = apps.get_model("meetings", "Meeting")
    AgendaItem = apps.get_model("meetings", "AgendaItem")
    db = schema_editor.connection.alias

    for topic in Topic.objects.using(db).exclude(due_date__isnull=True).iterator():
        meeting = Meeting.objects.using(db).filter(series_id=topic.series_id, date=topic.due_date).first()
        if meeting is None:
            meeting = Meeting.objects.using(db).create(series_id=topic.series_id, date=topic.due_date, title="")
        AgendaItem.objects.using(db).get_or_create(
            meeting_id=meeting.pk,
            topic_id=topic.pk,
            defaults={"working_text": "", "position": 0, "carried_forward": False},
        )


def restore_topic_due_dates(apps, schema_editor):
    Topic = apps.get_model("meetings", "Topic")
    AgendaItem = apps.get_model("meetings", "AgendaItem")
    db = schema_editor.connection.alias
    for topic in Topic.objects.using(db).all().iterator():
        first_item = (
            AgendaItem.objects.using(db).filter(topic_id=topic.pk)
            .select_related("meeting").order_by("meeting__date", "pk").first()
        )
        if first_item:
            Topic.objects.using(db).filter(pk=topic.pk).update(due_date=first_item.meeting.date)


class Migration(migrations.Migration):
    dependencies = [
        ("meetings", "0013_audit_event_series"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="agendaitem",
            name="assigned_to",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                related_name="assigned_meeting_agenda_items",
                to=settings.AUTH_USER_MODEL, verbose_name="Abweichend verantwortlich",
            ),
        ),
        migrations.AddField(
            model_name="topicsnapshot", name="responsible_name",
            field=models.CharField(blank=True, max_length=255, verbose_name="Verantwortlich"),
        ),
        migrations.RunPython(move_topic_due_dates_to_agenda, restore_topic_due_dates),
        migrations.RemoveField(model_name="topic", name="due_date"),
        migrations.AlterModelOptions(
            name="topic",
            options={"ordering": ["title"], "verbose_name": "Thema", "verbose_name_plural": "Themen"},
        ),
    ]
