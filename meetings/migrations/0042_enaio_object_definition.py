from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("meetings", "0041_enaio_agent")]

    operations = [
        migrations.AddField(model_name="enaiosettings", name="archive_name", field=models.CharField(blank=True, max_length=255, verbose_name="enaio-Schrankname")),
        migrations.AddField(model_name="enaiosettings", name="register_type_name", field=models.CharField(blank=True, max_length=255, verbose_name="Technischer Registertyp")),
        migrations.AddField(model_name="enaiosettings", name="register_name_field", field=models.CharField(blank=True, max_length=255, verbose_name="Technisches Register-Namensfeld")),
    ]
