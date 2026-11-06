from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("meetings", "0002_audit_event"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="topic",
            name="assigned_to",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                related_name="assigned_meeting_topics", to=settings.AUTH_USER_MODEL,
                verbose_name="Verantwortlich",
            ),
        ),
        migrations.AlterField(
            model_name="auditevent",
            name="action",
            field=models.CharField(
                choices=[
                    ("created", "Angelegt"), ("updated", "Geändert"),
                    ("archived", "Archiviert"), ("reopened", "Wieder geöffnet"),
                    ("transferred", "Übertragen"), ("attachment_added", "Anlage hinzugefügt"),
                    ("agenda_edited", "Agendatext geändert"),
                    ("finalized", "Besprechung abgeschlossen"),
                    ("comment_added", "Kommentar hinzugefügt"),
                ],
                max_length=24, verbose_name="Aktion",
            ),
        ),
        migrations.CreateModel(
            name="TopicComment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("body", models.TextField(max_length=5000, verbose_name="Kommentar")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Erstellt am")),
                ("author", models.ForeignKey(
                    blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                    related_name="meeting_topic_comments", to=settings.AUTH_USER_MODEL,
                )),
                ("topic", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE, related_name="comments",
                    to="meetings.topic",
                )),
            ],
            options={
                "verbose_name": "Themenkommentar",
                "verbose_name_plural": "Themenkommentare",
                "ordering": ["created_at", "pk"],
            },
        ),
    ]
