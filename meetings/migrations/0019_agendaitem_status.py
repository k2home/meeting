from django.db import migrations, models


def copy_legacy_topic_fields_to_agenda_items(apps, schema_editor):
    AgendaItem = apps.get_model("meetings", "AgendaItem")
    for item in AgendaItem.objects.select_related("topic").iterator():
        topic = item.topic
        if topic.status in {"open", "in_progress", "done"}:
            item.status = topic.status
        elif topic.status == "archived":
            item.status = "done"
        if not item.assigned_to_id and topic.assigned_to_id:
            item.assigned_to_id = topic.assigned_to_id
        item.save(update_fields=["status", "assigned_to"])


class Migration(migrations.Migration):
    dependencies = [("meetings", "0018_topic_completion_metadata")]

    operations = [
        migrations.AddField(
            model_name="agendaitem",
            name="status",
            field=models.CharField(
                choices=[("open", "Offen"), ("in_progress", "In Arbeit"), ("done", "Erledigt")],
                default="open",
                max_length=12,
                verbose_name="Bearbeitungsstand dieses Tagesordnungspunkts",
            ),
        ),
        migrations.RunPython(copy_legacy_topic_fields_to_agenda_items, migrations.RunPython.noop),
    ]
