from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("meetings", "0044_enaio_agent_logs")]

    operations = [
        migrations.AddField(
            model_name="enaiosettings",
            name="document_type_name",
            field=models.CharField(default="Standard", max_length=255, verbose_name="Technischer Dokumenttyp"),
        ),
    ]
