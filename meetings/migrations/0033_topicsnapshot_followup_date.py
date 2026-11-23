from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("meetings", "0032_organization_timezone"),
    ]

    operations = [
        migrations.AddField(
            model_name="topicsnapshot",
            name="followup_date",
            field=models.DateField(blank=True, null=True, verbose_name="Wiedervorlage am"),
        ),
    ]
