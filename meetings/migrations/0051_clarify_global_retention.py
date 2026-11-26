from django.core.validators import MinValueValidator
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("meetings", "0050_retained_agenda_entry"),
    ]

    operations = [
        migrations.AlterField(
            model_name="organizationsettings",
            name="retention_years",
            field=models.PositiveSmallIntegerField(
                default=10,
                validators=[MinValueValidator(1)],
                verbose_name="Zentrale Aufbewahrungsfrist (Jahre)",
                help_text="Gilt einheitlich für abgeschlossene Besprechungstermine und deren Protokolle. Zugleich Standard für archivierte Themen; einzelne Themen können eine abweichende Frist erhalten.",
            ),
        ),
    ]
