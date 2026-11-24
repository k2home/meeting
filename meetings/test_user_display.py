from django.contrib.auth import get_user_model
from django.test import TestCase

from .models import UserProfile
from .templatetags.meeting_user_tags import user_display_assignee

User = get_user_model()


class AssigneeDisplayTests(TestCase):
    def test_assignee_without_profile_uses_display_name(self):
        user = User.objects.create_user(
            username="assignee-without-profile",
            first_name="Ada",
            last_name="Lovelace",
            password="test-password",
        )

        self.assertEqual(user_display_assignee(user), "Ada Lovelace")

    def test_assignee_with_profile_includes_short_description(self):
        user = User.objects.create_user(
            username="assignee-with-profile",
            first_name="Grace",
            last_name="Hopper",
            password="test-password",
        )
        UserProfile.objects.create(user=user, short_description="IT")

        self.assertEqual(user_display_assignee(user), "IT – Grace Hopper")

    def test_missing_assignee_renders_as_empty_text(self):
        self.assertEqual(user_display_assignee(None), "")
