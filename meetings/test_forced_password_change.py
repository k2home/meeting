from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core import mail
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class ForcedPasswordChangeTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username="password-admin", password="AdminPassword1!")
        self.admin.groups.add(Group.objects.get_or_create(name="Admin")[0])

    def test_passwordless_user_creation_shows_temporary_password_and_forces_change(self):
        self.client.force_login(self.admin)
        response = self.client.post(reverse("management_user_new"), {
            "username": "new-password-user",
            "first_name": "Neu",
            "last_name": "Nutzer",
            "email": "",
            "short_description": "",
            "role": "user",
            "password1": "",
            "password2": "",
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("management_user_edit", args=[User.objects.get(username="new-password-user").pk]))
        account = User.objects.get(username="new-password-user")
        response = self.client.get(reverse("management_user_edit", args=[account.pk]))
        initial_password = response.context["initial_password"]["password"]
        self.assertContains(response, initial_password)
        self.assertTrue(account.check_password(initial_password))
        self.assertTrue(account.meeting_profile.must_change_password)
        self.assertNotIn("new_user_initial_password", self.client.session)

        self.client.logout()
        login_response = self.client.post(reverse("login"), {
            "username": account.username, "password": initial_password,
        })
        self.assertEqual(login_response.status_code, 302)
        self.assertEqual(login_response.url, reverse("dashboard"))
        forced_response = self.client.get(reverse("dashboard"))
        self.assertRedirects(forced_response, reverse("forced_password_change"))
        change_response = self.client.post(reverse("forced_password_change"), {
            "old_password": initial_password,
            "new_password1": "NewPersonalPassword1!",
            "new_password2": "NewPersonalPassword1!",
        })
        self.assertRedirects(change_response, reverse("dashboard"))
        account.refresh_from_db()
        self.assertTrue(account.check_password("NewPersonalPassword1!"))
        self.assertFalse(account.meeting_profile.must_change_password)

    def test_admin_reset_sends_no_email_and_requires_new_password_at_next_login(self):
        account = User.objects.create_user(username="reset-password-user", password="OldPassword1!")
        self.client.force_login(self.admin)
        response = self.client.post(reverse("management_user_password_reset", args=[account.pk]))
        self.assertRedirects(response, reverse("management_user_edit", args=[account.pk]))
        self.assertEqual(mail.outbox, [])
        account.refresh_from_db()
        self.assertTrue(account.check_password("OldPassword1!"))
        self.assertTrue(account.meeting_profile.must_change_password)

        self.client.logout()
        login_response = self.client.post(reverse("login"), {
            "username": account.username, "password": "OldPassword1!",
        })
        self.assertRedirects(login_response, reverse("dashboard"))
        forced_response = self.client.get(reverse("dashboard"))
        self.assertRedirects(forced_response, reverse("forced_password_change"))
        change_response = self.client.post(reverse("forced_password_change"), {
            "old_password": "OldPassword1!",
            "new_password1": "NewPersonalPassword1!",
            "new_password2": "NewPersonalPassword1!",
        })
        self.assertRedirects(change_response, reverse("dashboard"))
        account.refresh_from_db()
        self.assertTrue(account.check_password("NewPersonalPassword1!"))
        self.assertFalse(account.meeting_profile.must_change_password)
