from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from django.conf import settings
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
        except (ZoneInfoNotFoundError, TypeError):
            display_timezone = ZoneInfo(settings.TIME_ZONE)

        with timezone.override(display_timezone):
            return self.get_response(request)
