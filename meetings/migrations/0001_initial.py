# Generated for the initial version of the meetings application.
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="MeetingSeries",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=160, unique=True, verbose_name="Bezeichnung")),
                ("description", models.TextField(blank=True, verbose_name="Beschreibung")),
                ("active", models.BooleanField(default=True, verbose_name="Aktiv")),
                ("recurrence", models.CharField(choices=[("weekly", "Wöchentlich"), ("biweekly", "14-tägig"), ("monthly", "Monatlich")], default="monthly", max_length=12, verbose_name="Wiederholung")),
                ("weekday", models.PositiveSmallIntegerField(default=0, verbose_name="Wochentag (0=Mo)")),
                ("start_date", models.DateField(default=django.utils.timezone.localdate, verbose_name="Startdatum")),
                ("end_date", models.DateField(blank=True, null=True, verbose_name="Enddatum")),
            ],
            options={"verbose_name": "Besprechungsreihe", "verbose_name_plural": "Besprechungsreihen", "ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="Meeting",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("date", models.DateField(verbose_name="Termin")),
                ("title", models.CharField(blank=True, max_length=180, verbose_name="Titel")),
                ("finalized_at", models.DateTimeField(blank=True, null=True, verbose_name="Abgeschlossen am")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("series", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="meetings", to="meetings.meetingseries")),
            ],
            options={"verbose_name": "Besprechung", "verbose_name_plural": "Besprechungen", "ordering": ["date"]},
        ),
        migrations.CreateModel(
            name="Topic",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=240, verbose_name="Thema")),
                ("description", models.TextField(blank=True, verbose_name="Aktueller Stand")),
                ("due_date", models.DateField(blank=True, null=True, verbose_name="Fällig am")),
                ("status", models.CharField(choices=[("open", "Offen"), ("done", "Erledigt"), ("archived", "Archiviert")], default="open", max_length=12, verbose_name="Status")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("series", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="topics", to="meetings.meetingseries", verbose_name="Besprechungsreihe")),
            ],
            options={"verbose_name": "Thema", "verbose_name_plural": "Themen", "ordering": ["due_date", "title"]},
        ),
        migrations.CreateModel(
            name="TopicTransferHistory",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("transferred_at", models.DateTimeField(auto_now_add=True)),
                ("note", models.CharField(blank=True, max_length=500, verbose_name="Notiz")),
                ("from_series", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="outgoing_topic_transfers", to="meetings.meetingseries")),
                ("to_series", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="incoming_topic_transfers", to="meetings.meetingseries")),
                ("topic", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="transfer_history", to="meetings.topic")),
                ("transferred_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={"verbose_name": "Themenübertragung", "verbose_name_plural": "Themenübertragungen", "ordering": ["-transferred_at"]},
        ),
        migrations.CreateModel(
            name="AgendaItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("working_text", models.TextField(blank=True, verbose_name="Text für dieses Protokoll")),
                ("position", models.PositiveIntegerField(default=0)),
                ("carried_forward", models.BooleanField(default=False)),
                ("meeting", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="agenda_items", to="meetings.meeting")),
                ("topic", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="agenda_items", to="meetings.topic")),
            ],
            options={"ordering": ["position", "id"]},
        ),
        migrations.CreateModel(
            name="TopicSnapshot",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("topic_title", models.CharField(max_length=240)),
                ("text", models.TextField(blank=True)),
                ("status", models.CharField(max_length=12)),
                ("topic_id", models.PositiveBigIntegerField()),
                ("meeting", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="snapshots", to="meetings.meeting")),
            ],
            options={"ordering": ["id"]},
        ),
        migrations.CreateModel(
            name="TopicAttachment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("label", models.CharField(max_length=180, verbose_name="Bezeichnung")),
                ("uploaded_file", models.FileField(blank=True, upload_to="topic-files/%Y/%m/", verbose_name="Datei-Upload")),
                ("network_path", models.CharField(blank=True, max_length=1000, verbose_name="Netzwerkpfad / Link")),
                ("added_at", models.DateTimeField(auto_now_add=True)),
                ("topic", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="attachments", to="meetings.topic")),
            ],
        ),
        migrations.AddConstraint(
            model_name="meeting",
            constraint=models.UniqueConstraint(fields=("series", "date"), name="unique_series_meeting_date"),
        ),
        migrations.AddConstraint(
            model_name="agendaitem",
            constraint=models.UniqueConstraint(fields=("meeting", "topic"), name="unique_topic_per_meeting"),
        ),
    ]
