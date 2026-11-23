from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("meetings", "0037_enaio_filing"),
    ]

    operations = [
        migrations.CreateModel(
            name="EnaioSettings",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("root_folder_id", models.CharField(blank=True, max_length=64, verbose_name="enaio-Ordner-ID")),
                ("root_folder_type", models.PositiveIntegerField(default=0, verbose_name="enaio-Objekttyp")),
                ("root_folder_path", models.CharField(blank=True, max_length=1000, verbose_name="Ordnerpfad")),
                ("root_folder_name", models.CharField(blank=True, max_length=255, verbose_name="Ordnername")),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "enaio-Einstellung",
                "verbose_name_plural": "enaio-Einstellungen",
            },
        ),
    ]
