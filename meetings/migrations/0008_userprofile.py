from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("meetings", "0007_meeting_participants_initialized"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="UserProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("short_description", models.CharField(blank=True, max_length=80, verbose_name="Orgakürzel")),
                ("user", models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="meeting_profile",
                    to=settings.AUTH_USER_MODEL,
                    verbose_name="Benutzer",
                )),
            ],
            options={
                "verbose_name": "Benutzerprofil",
                "verbose_name_plural": "Benutzerprofile",
            },
        ),
    ]
