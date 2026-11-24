from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class LoginRememberMeTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="remember-test",
            password="A-Strong-Test-Password-123!",
        )

    def test_checked_remember_me_keeps_session_for_30_days(self):
        response = self.client.post(reverse("login"), {
            "username": self.user.username,
            "password": "A-Strong-Test-Password-123!",
            "remember_me": "1",
        })

        self.assertRedirects(response, reverse("dashboard"))
        self.assertFalse(self.client.session.get_expire_at_browser_close())
        self.assertEqual(self.client.session.get_expiry_age(), 30 * 24 * 60 * 60)

    def test_unchecked_remember_me_expires_session_when_browser_closes(self):
        response = self.client.post(reverse("login"), {
            "username": self.user.username,
            "password": "A-Strong-Test-Password-123!",
        })

        self.assertRedirects(response, reverse("dashboard"))
        self.assertTrue(self.client.session.get_expire_at_browser_close())
