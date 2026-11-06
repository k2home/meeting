from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("meetings", "0003_topic_responsibility_comments"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="meeting",
            name="participants",
            field=models.ManyToManyField(
                blank=True,
                related_name="meeting_participations",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Teilnehmer",
            ),
        ),
    ]
