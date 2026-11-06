from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("meetings", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="AuditEvent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("action", models.CharField(choices=[("created", "Angelegt"), ("updated", "Geändert"), ("archived", "Archiviert"), ("reopened", "Wieder geöffnet"), ("transferred", "Übertragen"), ("attachment_added", "Anlage hinzugefügt"), ("agenda_edited", "Agendatext geändert"), ("finalized", "Besprechung abgeschlossen")], max_length=24, verbose_name="Aktion")),
                ("summary", models.CharField(max_length=500, verbose_name="Beschreibung")),
                ("changes", models.JSONField(blank=True, default=dict, verbose_name="Änderungen")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Zeitpunkt")),
                ("actor", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="meeting_audit_events", to=settings.AUTH_USER_MODEL)),
                ("meeting", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="audit_events", to="meetings.meeting")),
                ("topic", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="audit_events", to="meetings.topic")),
            ],
            options={"verbose_name": "Änderungsverlauf", "verbose_name_plural": "Änderungsverläufe", "ordering": ["-created_at", "-pk"]},
        ),
    ]
