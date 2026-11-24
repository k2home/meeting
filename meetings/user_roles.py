from django.contrib.auth.models import Group

ADMIN_GROUP_NAME = "Admin"
AUDITOR_GROUP_NAME = "Auditor"
USER_ROLE_CHOICES = (("user", "Nutzer"), ("admin", "Admin"), ("auditor", "Auditor"))


def get_user_role(user):
    """Return the single global application role; superusers are always admins."""
    if user.is_superuser:
        return "admin"

    prefetched_groups = getattr(user, "_prefetched_objects_cache", {}).get("groups")
    if prefetched_groups is None:
        group_names = set(
            user.groups.filter(name__in=(ADMIN_GROUP_NAME, AUDITOR_GROUP_NAME))
            .values_list("name", flat=True)
        )
    else:
        group_names = {group.name for group in prefetched_groups}

    if ADMIN_GROUP_NAME in group_names:
        return "admin"
    if AUDITOR_GROUP_NAME in group_names:
        return "auditor"
    return "user"


def sync_user_role(user, role):
    """Synchronize global application groups and Django's staff flag."""
    if role not in dict(USER_ROLE_CHOICES):
        raise ValueError("Unbekannte Benutzerrolle.")
    admin_group, _ = Group.objects.get_or_create(name=ADMIN_GROUP_NAME)
    auditor_group, _ = Group.objects.get_or_create(name=AUDITOR_GROUP_NAME)
    if role == "admin":
        user.groups.add(admin_group)
        user.groups.remove(auditor_group)
    elif role == "auditor":
        user.groups.add(auditor_group)
        user.groups.remove(admin_group)
    else:
        user.groups.remove(admin_group, auditor_group)
    should_be_staff = user.is_superuser or role == "admin"
    if user.is_staff != should_be_staff:
        user.is_staff = should_be_staff
        user.save(update_fields=["is_staff"])


def sync_admin_access(user, enabled):
    """Backward-compatible wrapper for legacy setup and CSV imports."""
    sync_user_role(user, "admin" if enabled else "user")
