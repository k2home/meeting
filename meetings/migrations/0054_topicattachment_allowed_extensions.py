from django.core.validators import FileExtensionValidator
from django.db import migrations, models

import meetings.models


class Migration(migrations.Migration):

    dependencies = [
        ("meetings", "0053_remove_enaio_integration"),
    ]

    operations = [
        migrations.AlterField(
            model_name="topicattachment",
            name="uploaded_file",
            field=models.FileField(
                blank=True,
                help_text="Zulässig: PDF, DOCX, XLSX, PPTX, TXT, PNG und JPEG.",
                upload_to="topic-files/%Y/%m/",
                validators=[
                    meetings.models.validate_topic_attachment_size,
                    FileExtensionValidator(["pdf", "docx", "xlsx", "pptx", "txt", "png", "jpg", "jpeg"]),
                ],
                verbose_name="Datei-Upload",
            ),
        ),
    ]
