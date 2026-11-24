from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [("meetings", "0049_userprofile_must_change_password")]
    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="password_setup_expires_at",
            field=models.DateTimeField(blank=True, null=True, verbose_name="Frist für Passwortvergabe"),
        ),
    ]
