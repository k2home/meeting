from django.contrib.auth.models import Group, Permission
from django.db.models.signals import post_migrate, post_save
from django.dispatch import receiver

from .models import SeriesAccess


@receiver(post_migrate)
def grant_admin_role_permissions(sender, **kwargs):
    if sender.name != "meetings":
        return
    admin_group, _ = Group.objects.get_or_create(name="Admin")
    admin_group.permissions.set(Permission.objects.all())


@receiver(post_save, sender=SeriesAccess)
def remove_readers_from_series_participants(sender, instance, **kwargs):
    if instance.role != SeriesAccess.ROLE_READER:
        return
    from .models import Meeting
    for meeting in Meeting.objects.filter(series=instance.series, participants=instance.user).iterator():
        meeting.participants.remove(instance.user)
