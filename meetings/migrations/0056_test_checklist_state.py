from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("meetings", "0055_merge_global_retention_and_attachment_extensions"),
    ]

    operations = [
        migrations.CreateModel(
            name="TestChecklistState",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("state", models.JSONField(blank=True, default=dict, verbose_name="Prüfstatus")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Zuletzt geändert")),
            ],
            options={
                "verbose_name": "Testchecklisten-Status",
                "verbose_name_plural": "Testchecklisten-Status",
            },
        ),
    ]
