from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("meetings", "0051_merge_start_password_and_password_setup"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="auditevent",
            index=models.Index(fields=["scope", "-created_at"], name="audit_scope_created_idx"),
        ),
        migrations.AddIndex(
            model_name="auditevent",
            index=models.Index(fields=["series", "-created_at"], name="audit_series_created_idx"),
        ),
    ]
