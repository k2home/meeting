from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("meetings", "0036_allow_svg_organization_logo"),
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
