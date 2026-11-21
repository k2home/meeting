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
def user_display_with_login(user):
    """Display a person's name and, for administration, their login identifier."""
    return user_display_name_with_login(user)
