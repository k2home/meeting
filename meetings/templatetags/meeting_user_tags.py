from django import template

from meetings.user_display import user_display_name, user_display_name_with_login

register = template.Library()


@register.filter
def user_display(user):
    return user_display_name(user)


@register.filter
def user_display_context(user):
    """Display a short profile description where additional context helps."""
    return user_display_name(user, include_short_description=True)


@register.filter
def user_display_assignee(user):
    """Display an assignee's short description before their full name."""
    if user is None:
        return ""
    name = user_display_name(user)
    try:
        short_description = user.meeting_profile.short_description.strip()
    except ObjectDoesNotExist:
        short_description = ""
    return f"{short_description} – {name}" if short_description else name


@register.filter
def user_display_with_login(user):
    """Display a person's name and, for administration, their login identifier."""
    return user_display_name_with_login(user)


@register.filter
def audit_text(value):
    """Render escaped newline sequences from legacy audit values as real line breaks."""
    if not isinstance(value, str):
        return value
    return value.replace("\\r\\n", "\n").replace("\\n", "\n").replace("\\r", "\n")
