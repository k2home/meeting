from functools import wraps

from django.db.models import Q
from django.http import HttpResponseForbidden
from django.urls import reverse

from .models import Meeting, MeetingSeries, SeriesAccess, Topic
from .brand_colors import accessible_button_colors

ADMIN_GROUP = "Admin"
AUDITOR_GROUP = "Auditor"


def is_admin(user):
    return bool(user.is_authenticated and (
        user.is_superuser or user.groups.filter(name=ADMIN_GROUP).exists()
    ))


def is_auditor(user):
    return bool(user.is_authenticated and not is_admin(user) and user.groups.filter(name=AUDITOR_GROUP).exists())



def auditor_readonly(view):
    """Block state-changing POST requests from global auditors."""
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        if request.method == "POST" and is_auditor(request.user):
            return HttpResponseForbidden("Auditor*innen haben ausschließlich Lesezugriff.")
        return view(request, *args, **kwargs)
    return wrapped


def role_for_series(user, series):
    if not user.is_authenticated or series is None or is_auditor(user):
        return None
    return SeriesAccess.objects.filter(user=user, series=series).values_list("role", flat=True).first()


def is_moderator(user, series=None):
    if not user.is_authenticated or is_auditor(user):
        return False
    assignments = SeriesAccess.objects.filter(user=user, role=SeriesAccess.ROLE_MODERATOR)
    return assignments.filter(series=series).exists() if series is not None else assignments.exists()


def is_reader(user, series=None):
    if not user.is_authenticated or is_auditor(user):
    assignments = SeriesAccess.objects.filter(user=user, role=SeriesAccess.ROLE_READER)
    return assignments.filter(series=series).exists() if series is not None else assignments.exists()


def has_writable_series(user):
    if not user.is_authenticated or is_auditor(user):
        return False
    return SeriesAccess.objects.filter(user=user).exclude(role=SeriesAccess.ROLE_READER).exists()


def accessible_series(user):
    if not user.is_authenticated or is_auditor(user):
        return MeetingSeries.objects.none()
    return MeetingSeries.objects.filter(user_access__user=user)


def accessible_meetings(user):
    if not user.is_authenticated or is_auditor(user):
        return Meeting.objects.none()
    return Meeting.objects.filter(
        Q(series__in=accessible_series(user))
        | Q(archived_access__user=user)
    ).distinct()


def accessible_topics(user):
    if not user.is_authenticated or is_auditor(user):
        return Topic.objects.none()
    visible_meetings = accessible_meetings(user)
    return Topic.objects.filter(
        Q(series__in=accessible_series(user))
        | (Q(series__isnull=True) & Q(agenda_items__meeting__in=visible_meetings))
    ).distinct()


def can_reopen_meeting(user, meeting=None):
    return is_moderator(user, meeting.series if meeting else None)


def role_flags(request):
    if not request.user.is_authenticated:
        return {"is_admin": False, "is_moderator": False, "is_reader": False, "is_auditor": False}
    return {
        "is_admin": is_admin(request.user),
        "is_auditor": is_auditor(request.user),
        "is_moderator": is_moderator(request.user),
        "is_reader": is_reader(request.user) and not has_writable_series(request.user),
        "can_view_open_topics": not is_auditor(request.user) and SeriesAccess.objects.filter(
            user=request.user, role__in=[SeriesAccess.ROLE_PARTICIPANT, SeriesAccess.ROLE_MODERATOR]
        ).exists(),
    }


def organization_branding(request):
    """Stellt die zentrale Organisationseinheit in allen Templates bereit."""
    from .models import OrganizationSettings

    settings = OrganizationSettings.objects.filter(pk=1).first()
    logo_url = reverse("organization_logo") if settings and settings.logo else ""
    colors = OrganizationSettings.current_brand_colors()
    button_colors = {}
    for palette in ("light", "dark"):
        for name in ("primary", "secondary"):
            result = accessible_button_colors(colors[f"{name}_color_{palette}"])
            button_colors[f"{name}_button_bg_{palette}"] = result["background"]
            button_colors[f"{name}_button_text_{palette}"] = result["text"]
            button_colors[f"{name}_button_contrast_{palette}"] = result["contrast"]
    return {
        "organization_unit_name": OrganizationSettings.current_name(),
        "organization_unit_short_name": OrganizationSettings.current_short_name(),
        "organization_logo_url": logo_url,
        **colors,
        **button_colors,
    }
