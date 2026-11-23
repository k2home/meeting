import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("meetings", "0035_topicsnapshot_followup_series_name"),
    ]

    operations = [
        migrations.AlterField(
            model_name="organizationsettings",
            name="logo",
            field=models.FileField(
                blank=True,
                help_text="Optionales Logo für die Kopfzeile von Protokoll-PDFs. Unterstützte Formate: PNG, JPEG und SVG.",
                upload_to="organization/logo/",
                validators=[django.core.validators.FileExtensionValidator(["png", "jpg", "jpeg", "svg"])],
                verbose_name="Organisationslogo",
            ),
        ),
    ]
