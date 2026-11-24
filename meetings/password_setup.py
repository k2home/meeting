from datetime import timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import OrganizationSettings, UserProfile

PASSWORD_SETUP_TIMEOUT = timedelta(hours=24)

def start_password_setup(user):
    """Set the shared initial password and restart the 24-hour setup window."""
    user.set_password(OrganizationSettings.current_start_password())
    user.save(update_fields=["password"])
    profile, _ = UserProfile.objects.get_or_create(user=user)
    profile.must_change_password = True
    profile.password_setup_expires_at = timezone.now() + PASSWORD_SETUP_TIMEOUT
    profile.save(update_fields=["must_change_password", "password_setup_expires_at"])
    return profile

def expire_password_setup_if_due(user):
    """Deactivate accounts whose mandatory password setup window has elapsed."""
    try:
        profile = user.meeting_profile
    except UserProfile.DoesNotExist:
        return False
    if (not profile.must_change_password
            or profile.password_setup_expires_at is None
            or profile.password_setup_expires_at > timezone.now()):
        return False
    if user.is_active:
        user.is_active = False
        user.save(update_fields=["is_active"])
    return True

def expire_overdue_password_setups():
    """Bulk-expire all accounts whose mandatory password setup deadline elapsed."""
    now = timezone.now()
    user_ids = UserProfile.objects.filter(
        must_change_password=True,
        password_setup_expires_at__isnull=False,
        password_setup_expires_at__lte=now,
        user__is_active=True,
    ).values_list("user_id", flat=True)
    return get_user_model().objects.filter(pk__in=user_ids).update(is_active=False)
