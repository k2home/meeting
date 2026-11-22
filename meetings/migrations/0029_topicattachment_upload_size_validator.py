import meetings.models
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("meetings", "0028_upload_limit_and_series_name_recovery")]

    operations = [
        migrations.AlterField(
            model_name="topicattachment",
            name="uploaded_file",
            field=models.FileField(
                blank=True,
                upload_to="topic-files/%Y/%m/",
                validators=[meetings.models.validate_topic_attachment_size],
                verbose_name="Datei-Upload",
            ),
        ),
    ]
