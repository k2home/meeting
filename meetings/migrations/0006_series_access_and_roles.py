from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def create_roles_and_preserve_existing_access(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    User = apps.get_model(*settings.AUTH_USER_MODEL.split("."))
    MeetingSeries = apps.get_model("meetings", "MeetingSeries")
    SeriesAccess = apps.get_model("meetings", "SeriesAccess")
    db = schema_editor.connection.alias
    groups = {
        name: Group.objects.using(db).get_or_create(name=name)[0]
        for name in ("Nutzer*in", "Moderator*in", "Admin")
    }
    series_ids = list(MeetingSeries.objects.using(db).values_list("pk", flat=True))
    for user in User.objects.using(db).all():
        group = groups["Admin"] if user.is_staff or user.is_superuser else groups["Nutzer*in"]
        user.groups.add(group)
        if not user.is_staff and not user.is_superuser:
            SeriesAccess.objects.using(db).bulk_create(
                [SeriesAccess(user_id=user.pk, series_id=series_id) for series_id in series_ids],
                ignore_conflicts=True,
            )


class Migration(migrations.Migration):
    dependencies = [
        ("meetings", "0005_preserve_meetings_when_series_deleted"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="SeriesAccess",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("series", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="user_access", to="meetings.meetingseries", verbose_name="Besprechungsreihe")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="meeting_series_access", to=settings.AUTH_USER_MODEL, verbose_name="Benutzer")),
            ],
            options={"verbose_name": "Serienberechtigung", "verbose_name_plural": "Serienberechtigungen", "ordering": ["series__name", "user__username"]},
        ),
        migrations.AddConstraint(
            model_name="seriesaccess",
            constraint=models.UniqueConstraint(fields=("user", "series"), name="unique_user_series_access"),
        ),
        migrations.RunPython(create_roles_and_preserve_existing_access, migrations.RunPython.noop),
    ]
