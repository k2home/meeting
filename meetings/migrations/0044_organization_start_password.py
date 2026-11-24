from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("meetings", "0043_enaio_agent_job_leases")]

    operations = [
        migrations.AddField(
            model_name="organizationsettings",
            name="start_password",
            field=models.TextField(default="Neu", verbose_name="Startpasswort", help_text="Wird bei passwortloser Benutzeranlage, Passwort-Reset und Freischaltung verwendet."),
        ),
    ]
