from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from .management_views import ManagedUserCreateForm
from .views import testing_mode_context

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


class TestingModeBrowserTitleContextTests(TestCase):
    @patch("meetings.views._debian_testing_mode_enabled", return_value=True)
    def test_testing_mode_is_exposed_to_templates_when_enabled(self, _testing_mode):
        context = testing_mode_context(RequestFactory().get("/"))

        self.assertEqual(context, {"testing_mode": True})

    @patch("meetings.views._debian_testing_mode_enabled", return_value=False)
    def test_testing_mode_is_exposed_as_disabled_when_inactive(self, _testing_mode):
        context = testing_mode_context(RequestFactory().get("/"))

        self.assertEqual(context, {"testing_mode": False})
