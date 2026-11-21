from django.contrib.auth.models import Group, Permission
from django.db.models.signals import post_migrate
from django.dispatch import receiver


@receiver(post_migrate)
def grant_admin_role_permissions(sender, **kwargs):
    if sender.name != "meetings":
        return
    admin_group, _ = Group.objects.get_or_create(name="Admin")
    admin_group.permissions.set(Permission.objects.all())
    Group.objects.get_or_create(name="Nutzer*in")
    Group.objects.get_or_create(name="Moderator*in")
