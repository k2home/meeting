from django.contrib.auth.models import Group

ADMIN_GROUP_NAME = "Admin"


def sync_admin_access(user, enabled):
    """Keep the global Admin group and Django's staff flag in sync."""
    group, _ = Group.objects.get_or_create(name=ADMIN_GROUP_NAME)
    if enabled:
        user.groups.add(group)
    else:
        user.groups.remove(group)

    should_be_staff = user.is_superuser or enabled
    if user.is_staff != should_be_staff:
        user.is_staff = should_be_staff
        user.save(update_fields=["is_staff"])
