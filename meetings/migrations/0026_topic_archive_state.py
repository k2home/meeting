from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("meetings", "0025_series_validation_and_archived_access"),
    ]

    operations = [
        migrations.AddField(
            model_name="topic",
            name="archive_previous_status",
            field=models.CharField(blank=True, max_length=12, verbose_name="Status vor Archivierung"),
        ),
    ]
