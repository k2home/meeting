from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("meetings", "0039_enaio_folder_selection"),
    ]

    operations = [
        migrations.AddField(
            model_name="organizationsettings",
            name="logo_png",
            field=models.FileField(
                blank=True,
                help_text="Automatisch erzeugte PNG-Version für den PDF-Export.",
                upload_to="organization/logo/converted/",
                verbose_name="Organisationslogo (PNG)",
            ),
        ),
    ]
