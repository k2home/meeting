from django.db import migrations, models


def migrate_global_roles_to_series(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    SeriesAccess = apps.get_model("meetings", "SeriesAccess")
    db = schema_editor.connection.alias

    role_groups = {
        group.name: group.pk
        for group in Group.objects.using(db).filter(
            name__in=["Leser*in", "Moderator*in", "Nutzer*in", "Teilnehmer*in"]
        )
    }
    through = apps.get_model("auth", "User_groups")
    memberships = set(
        through.objects.using(db).filter(
            group_id__in=role_groups.values()
        ).values_list("user_id", "group_id")
    )

    for assignment in SeriesAccess.objects.using(db).all().iterator():
        user_id = assignment.user_id
        if role_groups.get("Leser*in") and (user_id, role_groups["Leser*in"]) in memberships:
            role = "reader"
        elif role_groups.get("Moderator*in") and (user_id, role_groups["Moderator*in"]) in memberships:
            role = "moderator"
        else:
            role = "participant"
        SeriesAccess.objects.using(db).filter(pk=assignment.pk).update(role=role)

    Group.objects.using(db).filter(
        name__in=["Leser*in", "Moderator*in", "Nutzer*in", "Teilnehmer*in"]
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("meetings", "0008_userprofile"),
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.AddField(
            model_name="seriesaccess",
            name="role",
            field=models.CharField(
                choices=[
                    ("participant", "Teilnehmer*in"),
                    ("moderator", "Moderator*in"),
                    ("reader", "Leser*in"),
                ],
                default="participant",
                max_length=16,
                verbose_name="Rolle",
            ),
        ),
        migrations.RunPython(migrate_global_roles_to_series, migrations.RunPython.noop),
    ]
