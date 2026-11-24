from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("meetings", "0048_auditevent_scope"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="must_change_password",
            field=models.BooleanField(default=False, verbose_name="Passwort muss geändert werden"),
        ),
    ]
