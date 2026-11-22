from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [("meetings", "0020_remove_topic_description")]

    operations = [
        migrations.AddField(
            model_name="agendaitem",
            name="followup_of",
            field=models.OneToOneField(
                blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                related_name="followup_item", to="meetings.agendaitem",
            ),
        ),
    ]
