from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.db.models.signals import m2m_changed, post_migrate
from django.dispatch import receiver


@receiver(post_migrate)
def grant_admin_role_permissions(sender, **kwargs):
    if sender.name != "meetings":
        return
    admin_group, _ = Group.objects.get_or_create(name="Admin")
    admin_group.permissions.set(Permission.objects.all())
    Group.objects.get_or_create(name="Nutzer*in")
    Group.objects.get_or_create(name="Moderator*in")
    Group.objects.get_or_create(name="Leser*in")



@receiver(m2m_changed, sender=get_user_model().groups.through)
def remove_readers_from_meeting_participants(sender, instance, action, reverse, pk_set, **kwargs):
    """Remove users from meeting participant lists when they receive reader role."""
    if action != "post_add":
        return
    reader_group = Group.objects.filter(name="Leser*in").first()
    if reader_group is None:
        return
    if reverse:
        if instance.pk != reader_group.pk:
            return
        user_ids = pk_set or ()
    else:
        if reader_group.pk not in (pk_set or ()):
            return
        user_ids = [instance.pk]
    from .models import Meeting
    for meeting in Meeting.objects.filter(participants__id__in=user_ids).distinct().iterator():
        meeting.participants.remove(*user_ids)
