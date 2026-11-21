from django import template

from meetings.user_display import user_display_name

register = template.Library()


@register.filter
def user_display(user):
    return user_display_name(user)
