from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("meetings", "0047_enaio_diagnostic_reports"),
    ]

    operations = [
        migrations.AddField(
            model_name="auditevent",
            name="scope",
            field=models.CharField(
                choices=[("series", "Besprechungsreihe"), ("system", "System")],
                db_index=True,
                default="series",
                max_length=12,
                verbose_name="Bereich",
            ),
        ),
    ]
