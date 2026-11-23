# Generated for the per-user enaio background agent.
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("meetings", "0040_organization_logo_png"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="EnaioAgent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("device_token_hash", models.CharField(blank=True, max_length=64)),
                ("pairing_code_hash", models.CharField(blank=True, max_length=64)),
                ("pairing_expires_at", models.DateTimeField(blank=True, null=True)),
                ("device_name", models.CharField(blank=True, max_length=120)),
                ("last_seen_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="enaio_agent", to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
