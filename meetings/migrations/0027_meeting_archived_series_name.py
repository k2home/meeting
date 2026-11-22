from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("meetings", "0026_topic_archive_state"),
    ]

    operations = [
        migrations.AddField(
            model_name="meeting",
            name="archived_series_name",
            field=models.CharField(
                blank=True,
                max_length=160,
                verbose_name="Ursprüngliche Besprechungsreihe",
            ),
        ),
    ]
