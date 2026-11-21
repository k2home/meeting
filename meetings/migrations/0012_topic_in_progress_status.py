from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("meetings", "0011_organization_short_name"),
    ]

    operations = [
        migrations.AlterField(
            model_name="topic",
            name="status",
            field=models.CharField(
                choices=[
                    ("open", "Offen"),
                    ("in_progress", "In Arbeit"),
                    ("done", "Erledigt"),
                    ("archived", "Archiviert"),
                ],
                default="open",
                max_length=12,
                verbose_name="Status",
            ),
        ),
    ]
