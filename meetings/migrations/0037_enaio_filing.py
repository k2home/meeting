import django.conf
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(django.conf.settings.AUTH_USER_MODEL),
        ("meetings", "0036_allow_svg_organization_logo"),
    ]

    operations = [
        migrations.CreateModel(
            name="EnaioFilingTarget",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("object_id", models.CharField(max_length=64, verbose_name="enaio-Ordner-ID")),
                ("object_type", models.PositiveIntegerField(default=0, verbose_name="enaio-Objekttyp")),
                ("display_path", models.CharField(max_length=1000, verbose_name="Ordnerpfad")),
                ("display_name", models.CharField(blank=True, max_length=255, verbose_name="Ordnername")),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="enaio_filing_target", to=django.conf.settings.AUTH_USER_MODEL)),
            ],
            options={"verbose_name": "Persönliches enaio-Ablageziel", "verbose_name_plural": "Persönliche enaio-Ablageziele"},
        ),
        migrations.CreateModel(
            name="EnaioTransfer",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("token_hash", models.CharField(max_length=64, unique=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("expires_at", models.DateTimeField()),
                ("consumed_at", models.DateTimeField(blank=True, null=True)),
                ("status", models.CharField(choices=[("pending", "Ausstehend"), ("completed", "Abgeschlossen"), ("failed", "Fehlgeschlagen")], default="pending", max_length=12)),
                ("error_message", models.CharField(blank=True, max_length=500)),
                ("meeting", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="enaio_transfers", to="meetings.meeting")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="enaio_transfers", to=django.conf.settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]
