from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("meetings", "0038_enaio_settings"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="EnaioFolderSelection",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("token_hash", models.CharField(max_length=64, unique=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("expires_at", models.DateTimeField()),
                ("consumed_at", models.DateTimeField(blank=True, null=True)),
                ("selected_folder_id", models.CharField(blank=True, max_length=64)),
                ("selected_folder_type", models.PositiveIntegerField(default=0)),
                ("selected_folder_name", models.CharField(blank=True, max_length=255)),
                ("selected_folder_path", models.CharField(blank=True, max_length=1000)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="enaio_folder_selections", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]
