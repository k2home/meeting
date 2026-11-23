import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("meetings", "0033_topicsnapshot_followup_date"),
    ]

    operations = [
        migrations.AddField(
            model_name="organizationsettings",
            name="logo",
            field=models.FileField(
                blank=True,
                help_text="Optionales Logo für die Kopfzeile von Protokoll-PDFs. Empfohlenes Format: PNG oder JPEG.",
                upload_to="organization/logo/",
                validators=[django.core.validators.FileExtensionValidator(["png", "jpg", "jpeg"])],
                verbose_name="Organisationslogo",
            ),
        ),
    ]
