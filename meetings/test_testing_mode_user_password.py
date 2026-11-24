from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from .management_views import ManagedUserCreateForm

User = get_user_model()


class TestingModeUserPasswordTests(TestCase):
    @patch("meetings.management_views._testing_mode_enabled", return_value=True)
    def test_new_user_accepts_arbitrary_non_empty_password_in_testing_mode(self, _testing_mode):
        form = ManagedUserCreateForm(data={
            "username": "test-user",
            "password1": "x",
            "password2": "x",
        })

        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()

        self.assertTrue(user.check_password("x"))

    @patch("meetings.management_views._testing_mode_enabled", return_value=False)
    def test_new_user_still_obeys_password_policy_outside_testing_mode(self, _testing_mode):
        form = ManagedUserCreateForm(data={
            "username": "regular-user",
            "password1": "x",
            "password2": "x",
        })

        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)

    @patch("meetings.management_views._testing_mode_enabled", return_value=True)
    def test_passwords_must_still_match_in_testing_mode(self, _testing_mode):
        form = ManagedUserCreateForm(data={
            "username": "mismatched-user",
            "password1": "x",
            "password2": "y",
        })

        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)
