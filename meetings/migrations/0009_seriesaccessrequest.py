from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("meetings", "0008_userprofile"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="SeriesAccessRequest",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("requested_role", models.CharField(choices=[("participant", "Teilnehmer*in"), ("moderator", "Moderator*in"), ("reader", "Leser*in")], max_length=16, verbose_name="Beantragte Berechtigung")),
                ("status", models.CharField(choices=[("pending", "Offen"), ("approved", "Genehmigt"), ("rejected", "Abgelehnt")], default="pending", max_length=12, verbose_name="Status")),
                ("decision_note", models.CharField(blank=True, max_length=500, verbose_name="Begründung")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("decided_at", models.DateTimeField(blank=True, null=True)),
                ("decided_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="decided_series_access_requests", to=settings.AUTH_USER_MODEL)),
                ("series", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="access_requests", to="meetings.meetingseries")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="series_access_requests", to=settings.AUTH_USER_MODEL)),
            ],
            options={"verbose_name": "Berechtigungsantrag", "verbose_name_plural": "Berechtigungsanträge", "ordering": ["created_at", "pk"]},
        ),
        migrations.AddConstraint(
            model_name="seriesaccessrequest",
            constraint=models.UniqueConstraint(condition=models.Q(("status", "pending")), fields=("user", "series"), name="unique_pending_series_access_request"),
        ),
    ]
