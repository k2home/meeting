from django.core.exceptions import ObjectDoesNotExist


def user_display_name(user):
    """Return a user's public display name without changing their login name."""
    if user is None:
        return ""
    name = user.get_full_name().strip() or user.get_username()
    try:
        short_description = user.meeting_profile.short_description.strip()
    except ObjectDoesNotExist:
        short_description = ""
    return f"{name} ({short_description})" if short_description else name
