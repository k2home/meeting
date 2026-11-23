from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("meetings", "0031_alter_seriesaccessrequest_requested_role"),
    ]

    operations = [
        migrations.AddField(
            model_name="organizationsettings",
            name="timezone",
            field=models.CharField(
                default="Europe/Berlin",
                help_text="Zeitzone für die Anzeige von Datums- und Uhrzeitangaben, z. B. Europe/Berlin.",
                max_length=64,
                verbose_name="Zeitzone",
            ),
        ),
    ]
