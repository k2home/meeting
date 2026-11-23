from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [("meetings", "0043_enaio_agent_job_leases")]

    operations = [
        migrations.CreateModel(
            name="EnaioAgentLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("level", models.CharField(choices=[("DEBUG", "Debug"), ("INFO", "Info"), ("WARNING", "Warning"), ("ERROR", "Error")], default="INFO", max_length=10)),
                ("message", models.TextField(max_length=4000)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("agent", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="logs", to="meetings.enaioagent")),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.AddIndex(
            model_name="enaioagentlog",
            index=models.Index(fields=["-created_at"], name="enaio_log_created_idx"),
        ),
    ]
