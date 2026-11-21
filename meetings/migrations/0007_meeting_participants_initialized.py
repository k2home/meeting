from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("meetings", "0006_series_access_and_roles"),
    ]

    operations = [
        migrations.AddField(
            model_name="meeting",
            name="participants_initialized",
            field=models.BooleanField(default=False, verbose_name="Teilnehmer-Voreinstellung angewendet"),
        ),
    ]
