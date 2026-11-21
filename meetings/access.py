from .models import Meeting, MeetingSeries, SeriesAccess, Topic

ADMIN_GROUP = "Admin"
MODERATOR_GROUP = "Moderator*in"
USER_GROUP = "Nutzer*in"


def is_admin(user):
    return bool(user.is_authenticated and (
        user.is_superuser or user.is_staff or user.groups.filter(name=ADMIN_GROUP).exists()
    ))


def is_moderator(user):
    return bool(user.is_authenticated and (
        is_admin(user) or user.groups.filter(name=MODERATOR_GROUP).exists()
    ))


def accessible_series(user):
    if is_admin(user):
        return MeetingSeries.objects.all()
    # Compatibility for installations/tests with no assignments yet.
    if not SeriesAccess.objects.exists():
        return MeetingSeries.objects.all()
    return MeetingSeries.objects.filter(user_access__user=user)


def accessible_topics(user):
    if is_admin(user):
        return Topic.objects.all()
    return Topic.objects.filter(series__in=accessible_series(user))


def accessible_meetings(user):
    if is_admin(user):
        return Meeting.objects.all()
    return Meeting.objects.filter(series__in=accessible_series(user))


def can_reopen_meeting(user):
    return is_moderator(user)

def role_flags(request):
    if not request.user.is_authenticated:
        return {"is_admin": False, "is_moderator": False}
    return {"is_admin": is_admin(request.user), "is_moderator": is_moderator(request.user)}
