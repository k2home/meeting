from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("meetings", "0004_meeting_participants"),
    ]

    operations = [
        migrations.AlterField(
            model_name="meeting",
            name="series",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="meetings",
                to="meetings.meetingseries",
            ),
        ),
    ]
