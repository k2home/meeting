from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("meetings", "0049_topic_retention"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="RetainedAgendaEntry",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("original_meeting_id", models.PositiveBigIntegerField(db_index=True)),
                ("original_series_id", models.PositiveBigIntegerField(blank=True, db_index=True, null=True)),
                ("meeting_date", models.DateField(verbose_name="Ursprünglicher Besprechungstermin")),
                ("series_name", models.CharField(blank=True, max_length=160, verbose_name="Ursprüngliche Besprechungsreihe")),
                ("working_text", models.TextField(blank=True)),
                ("status", models.CharField(choices=[("open", "Offen"), ("in_progress", "In Arbeit"), ("done", "Erledigt")], default="open", max_length=12)),
                ("responsible_name", models.CharField(blank=True, max_length=255)),
                ("position", models.PositiveIntegerField(default=0)),
                ("access_users", models.ManyToManyField(blank=True, related_name="retained_agenda_entries", to=settings.AUTH_USER_MODEL)),
                ("topic", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="retained_agenda_entries", to="meetings.topic")),
            ],
            options={
                "ordering": ["-meeting_date", "position", "pk"],
                "constraints": [
                    models.UniqueConstraint(fields=("topic", "original_meeting_id"), name="unique_retained_agenda_topic_meeting"),
                ],
            },
        ),
    ]
