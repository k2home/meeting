from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("meetings", "0042_enaio_object_definition")]

    operations = [
        migrations.AddField(
            model_name="enaiofolderselection",
            name="agent_lease_token",
            field=models.CharField(blank=True, max_length=64),
        ),
        migrations.AddField(
            model_name="enaiofolderselection",
            name="agent_lease_expires_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="enaiofolderselection",
            name="error_message",
            field=models.CharField(blank=True, max_length=500),
        ),
        migrations.AddField(
            model_name="enaiotransfer",
            name="agent_lease_token",
            field=models.CharField(blank=True, max_length=64),
        ),
        migrations.AddField(
            model_name="enaiotransfer",
            name="agent_lease_expires_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
