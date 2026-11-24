from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("meetings", "0047_enaio_diagnostic_reports"),
    ]

    operations = [
        migrations.AddField(
            model_name="topic",
            name="priority",
            field=models.CharField(
                choices=[
                    ("low", "Niedrig"),
                    ("normal", "Normal"),
                    ("high", "Hoch"),
                    ("urgent", "Dringend"),
                ],
                default="normal",
                max_length=10,
                verbose_name="Priorität",
            ),
        ),
    ]
