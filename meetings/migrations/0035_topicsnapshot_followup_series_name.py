from django.db import migrations, models


def populate_followup_series_names(apps, schema_editor):
    TopicSnapshot = apps.get_model("meetings", "TopicSnapshot")
    AgendaItem = apps.get_model("meetings", "AgendaItem")
    Meeting = apps.get_model("meetings", "Meeting")

    for snapshot in TopicSnapshot.objects.filter(followup_date__isnull=False, followup_series_name="").iterator():
        source_item = AgendaItem.objects.filter(
            meeting_id=snapshot.meeting_id,
            topic_id=snapshot.topic_id,
        ).first()
        if not source_item:
            continue
        followup = AgendaItem.objects.filter(followup_of_id=source_item.pk).select_related("meeting").first()
        if not followup:
            continue
        target_meeting = followup.meeting
        series_name = ""
        if target_meeting.series_id:
            series_name = target_meeting.series.name
        else:
            series_name = target_meeting.archived_series_name or "Gelöschte Besprechungsreihe"
        TopicSnapshot.objects.filter(pk=snapshot.pk).update(followup_series_name=series_name)


class Migration(migrations.Migration):

    dependencies = [
        ("meetings", "0034_organization_logo"),
    ]

    operations = [
        migrations.AddField(
            model_name="topicsnapshot",
            name="followup_series_name",
            field=models.CharField(blank=True, max_length=160, verbose_name="Besprechungsreihe der Wiedervorlage"),
        ),
        migrations.RunPython(populate_followup_series_names, migrations.RunPython.noop),
    ]
