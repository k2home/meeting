from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from django.conf import settings
from django.contrib.auth import logout
from django.utils import timezone


class OrganizationTimezoneMiddleware:
    """Aktiviert die in den Organisationseinstellungen gewählte Zeitzone."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        configured_timezone = settings.TIME_ZONE
        from .models import OrganizationSettings

        configured_timezone = (
            OrganizationSettings.objects.filter(pk=1)
            .values_list("timezone", flat=True)
            .first()
            or configured_timezone
        )
        try:
            display_timezone = ZoneInfo(configured_timezone)
        except (ZoneInfoNotFoundError, TypeError, ValueError):
            display_timezone = ZoneInfo(settings.TIME_ZONE)

        with timezone.override(display_timezone):
            return self.get_response(request)

 
class EnforcePasswordChangeMiddleware:
    """Restrict marked accounts to the password-change page until updated."""

    ALLOWED_PATHS = {"/konto/passwort-aendern/", "/logout/"}

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        from .password_setup import expire_overdue_password_setups
        expire_overdue_password_setups()
        user = getattr(request, "user", None)
        if user is not None and user.is_authenticated:
            from .password_setup import expire_password_setup_if_due
            from django.shortcuts import redirect
            if expire_password_setup_if_due(user):
                logout(request)
                return redirect("login")
            if request.path_info not in self.ALLOWED_PATHS:
                profile = getattr(user, "meeting_profile", None)
                if (profile is not None and profile.must_change_password) or not user.has_usable_password():
                    return redirect("/konto/passwort-aendern/")
        return self.get_response(request)
