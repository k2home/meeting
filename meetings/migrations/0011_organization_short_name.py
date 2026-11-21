from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("meetings", "0010_organization_settings"),
    ]

    operations = [
        migrations.AddField(
            model_name="organizationsettings",
            name="short_name",
            field=models.CharField(
                blank=True,
                default="MM",
                help_text='Kompakte Anzeige im eingeklappten Seitenmenü, zum Beispiel „FB 20“ oder „FB20“.',
                max_length=24,
                verbose_name="Kurzbezeichnung",
            ),
        ),
    ]
