from django.core.exceptions import ObjectDoesNotExist


def user_display_name(user, include_short_description=False):
    """Return a person's display name; login names are only a fallback."""
    if user is None:
        return ""
    name = user.get_full_name().strip() or user.get_username()
    if not include_short_description:
        return name
    try:
        short_description = user.meeting_profile.short_description.strip()
    except ObjectDoesNotExist:
        short_description = ""
    return f"{name} ({short_description})" if short_description else name


def user_display_name_with_login(user):
    """Return the display name with the login name as an admin-only identifier."""
    if user is None:
        return ""
    name = user_display_name(user)
    if not name or name == user.get_username():
        return name
    return f"{name} ({user.get_username()})"
