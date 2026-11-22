from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("meetings", "0021_agendaitem_followup_of"),
    ]

    operations = [
        migrations.AlterField(
            model_name="topic",
            name="series",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="topics",
                to="meetings.meetingseries",
            ),
        ),
    ]
