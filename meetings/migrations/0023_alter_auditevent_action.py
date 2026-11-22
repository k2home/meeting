from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("meetings", "0022_alter_topic_series"),
    ]

    operations = [
        migrations.AlterField(
            model_name="auditevent",
            name="action",
            field=models.CharField(
                choices=[
                    ("created", "Angelegt"),
                    ("updated", "Geändert"),
                    ("archived", "Archiviert"),
                    ("reopened", "Wieder geöffnet"),
                    ("transferred", "Übertragen"),
                    ("attachment_added", "Anlage hinzugefügt"),
                    ("agenda_edited", "Agendatext geändert"),
                    ("finalized", "Besprechung abgeschlossen"),
                    ("comment_added", "Kommentar hinzugefügt"),
                    ("deleted", "Gelöscht"),
                    ("series_extended", "Terminreihe verlängert"),
                    ("series_reset", "Termine neu aufgesetzt"),
                ],
                max_length=24,
                verbose_name="Aktion",
            ),
        ),
    ]
