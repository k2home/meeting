from functools import wraps

from django.db.models import Exists, OuterRef, Q
from django.http import HttpResponseForbidden
from django.urls import reverse

from .models import Meeting, MeetingSeries, RetainedAgendaEntry, SeriesAccess, Topic
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
    if not user.is_authenticated:
        return False
    if is_auditor(user):
        return False
    assignments = SeriesAccess.objects.filter(user=user, role=SeriesAccess.ROLE_READER)
    return assignments.filter(series=series).exists() if series is not None else assignments.exists()


def has_writable_series(user):
    if not user.is_authenticated or is_auditor(user):
        return False
    return SeriesAccess.objects.filter(user=user).exclude(role=SeriesAccess.ROLE_READER).exists()


def accessible_series(user):
    if not user.is_authenticated:
        return MeetingSeries.objects.none()
    if is_auditor(user):
        return MeetingSeries.objects.none()
    return MeetingSeries.objects.filter(user_access__user=user)


def accessible_meetings(user):
    if not user.is_authenticated:
        return Meeting.objects.none()
    if is_auditor(user):
        return Meeting.objects.none()
    return Meeting.objects.filter(
        Q(series__in=accessible_series(user))
        | Q(archived_access__user=user)
    ).distinct()


def accessible_retained_agenda_entries(user):
    """Limit deleted-meeting history to the original meeting's access scope."""
    if not user.is_authenticated or is_auditor(user):
        return RetainedAgendaEntry.objects.none()
    original_series_exists = MeetingSeries.objects.filter(pk=OuterRef("original_series_id"))
    return RetainedAgendaEntry.objects.annotate(
        _original_series_exists=Exists(original_series_exists)
    ).filter(
        Q(original_series_id__in=accessible_series(user).values("pk"))
        | Q(_original_series_exists=False, access_users=user)
    ).distinct()


def accessible_topics(user):
    if not user.is_authenticated:
        return Topic.objects.none()
    if is_auditor(user):
        return Topic.objects.none()
    visible_meetings = accessible_meetings(user)
    retained_topic_ids = accessible_retained_agenda_entries(user).values("topic_id")
    return Topic.objects.filter(
        Q(series__in=accessible_series(user))
        | (Q(series__isnull=True) & Q(agenda_items__meeting__in=visible_meetings))
        | (Q(series__isnull=True) & Q(pk__in=retained_topic_ids))
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
    """Stellt Organisationsbranding aus dem bereits geladenen Request-Datensatz bereit."""
    from .models import OrganizationSettings

    if hasattr(request, "_organization_settings"):
        organization = request._organization_settings
    else:
        organization = OrganizationSettings.objects.filter(pk=1).first()

    defaults = {
        "primary_color": "#00549F",
        "secondary_color": "#8FC5FF",
        "tertiary_color": "#FFCC00",
    }
    colors = {}
    for name, default in defaults.items():
        base = getattr(organization, name, "") or default
        colors[name] = base
        colors[f"{name}_light"] = (getattr(organization, f"{name}_light", "") or base) if organization else base
        colors[f"{name}_dark"] = (getattr(organization, f"{name}_dark", "") or base) if organization else base

    button_colors = {}
    for palette in ("light", "dark"):
        for name in ("primary", "secondary"):
            result = accessible_button_colors(colors[f"{name}_color_{palette}"])
            button_colors[f"{name}_button_bg_{palette}"] = result["background"]
            button_colors[f"{name}_button_text_{palette}"] = result["text"]
            button_colors[f"{name}_button_contrast_{palette}"] = result["contrast"]

    return {
        "organization_unit_name": organization.name.strip() if organization and organization.name else "",
        "organization_unit_short_name": organization.short_name.strip() if organization and organization.short_name else "MM",
        "organization_logo_url": reverse("organization_logo") if organization and organization.logo else "",
        **colors,
        **button_colors,
    }
