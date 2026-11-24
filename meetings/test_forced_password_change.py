from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core import mail
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import UserProfile

User = get_user_model()


class ForcedPasswordChangeTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username="password-admin", password="AdminPassword1!")
        self.admin.groups.add(Group.objects.get_or_create(name="Admin")[0])

    def test_passwordless_user_creation_and_initial_password_login(self):
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
        self.assertRedirects(response, reverse("management_users"))
        self.assertEqual(mail.outbox, [])
        account = User.objects.get(username="new-password-user")
        self.assertTrue(account.has_usable_password())
        self.assertTrue(account.check_password("Neu"))
        self.assertTrue(account.meeting_profile.must_change_password)
        self.assertIsNotNone(account.meeting_profile.password_setup_expires_at)

        self.client.logout()
        login_response = self.client.post(reverse("login"), {"username": account.username, "password": "Neu"})
        self.assertEqual(login_response.status_code, 302)
        self.assertEqual(login_response.url, reverse("dashboard"))
        forced_response = self.client.get(reverse("dashboard"))
        self.assertRedirects(forced_response, reverse("forced_password_change"))
        change_response = self.client.post(reverse("forced_password_change"), {
            "new_password1": "IndependentLongPassword9!",
            "new_password2": "IndependentLongPassword9!",
        })
        self.assertRedirects(change_response, reverse("dashboard"))
        account.refresh_from_db()
        self.assertTrue(account.check_password("IndependentLongPassword9!"))
        self.assertFalse(account.meeting_profile.must_change_password)

    def test_admin_reset_sends_no_email_and_requires_new_password_at_next_login(self):
        account = User.objects.create_user(username="reset-password-user", password="OldPassword1!")
        self.client.force_login(self.admin)
        response = self.client.post(reverse("management_user_password_reset", args=[account.pk]))
        self.assertRedirects(response, reverse("management_user_edit", args=[account.pk]))
        self.assertEqual(mail.outbox, [])
        account.refresh_from_db()
        self.assertTrue(account.has_usable_password())
        self.assertTrue(account.check_password("Neu"))
        self.assertTrue(account.meeting_profile.must_change_password)
        self.assertIsNotNone(account.meeting_profile.password_setup_expires_at)

        self.client.logout()
        login_response = self.client.post(reverse("login"), {
            "username": account.username, "password": "Neu",
        })
        self.assertEqual(login_response.status_code, 302)
        self.assertEqual(login_response.url, reverse("dashboard"))
        forced_response = self.client.get(reverse("dashboard"))
        self.assertRedirects(forced_response, reverse("forced_password_change"))
        change_response = self.client.post(reverse("forced_password_change"), {
            "new_password1": "IndependentLongPassword9!",
            "new_password2": "IndependentLongPassword9!",
        })
        self.assertRedirects(change_response, reverse("dashboard"))
        account.refresh_from_db()
        self.assertTrue(account.check_password("IndependentLongPassword9!"))
        self.assertFalse(account.meeting_profile.must_change_password)
        self.assertIsNone(account.meeting_profile.password_setup_expires_at)

    def test_expired_setup_window_deactivates_account_and_blocks_login(self):
        account = User.objects.create_user(username="expired-setup-user", password="Neu")
        UserProfile.objects.create(
            user=account, must_change_password=True,
            password_setup_expires_at=timezone.now() - timedelta(seconds=1),
        )
        response = self.client.post(reverse("login"), {
            "username": f" {account.username} ", "password": "Neu",
        })
        self.assertEqual(response.status_code, 200)
        account.refresh_from_db()
        self.assertFalse(account.is_active)

    def test_login_expiry_check_does_not_deactivate_unrelated_accounts(self):
        attempted = User.objects.create_user(username="attempted-expired-user", password="Neu")
        unrelated = User.objects.create_user(username="unrelated-expired-user", password="Neu")
        expired_at = timezone.now() - timedelta(seconds=1)
        for account in (attempted, unrelated):
            UserProfile.objects.create(
                user=account, must_change_password=True,
                password_setup_expires_at=expired_at,
            )

        self.client.post(reverse("login"), {
            "username": attempted.username, "password": "Neu",
        })

        attempted.refresh_from_db()
        unrelated.refresh_from_db()
        self.assertFalse(attempted.is_active)
        self.assertTrue(unrelated.is_active)

    def test_admin_reactivation_resets_password_and_starts_new_24_hour_window(self):
        account = User.objects.create_user(username="reactivate-user", password="OldPassword1!", is_active=False)
        self.client.force_login(self.admin)
        response = self.client.post(reverse("management_user_edit", args=[account.pk]), {
            "username": account.username, "first_name": "", "last_name": "", "email": "",
            "is_active": "true", "role": "user", "short_description": "",
        })
        self.assertRedirects(response, reverse("management_users"))
        account.refresh_from_db()
        self.assertTrue(account.is_active)
        self.assertTrue(account.check_password("Neu"))
        self.assertTrue(account.meeting_profile.must_change_password)
        self.assertGreater(account.meeting_profile.password_setup_expires_at, timezone.now())
        self.assertLessEqual(
            account.meeting_profile.password_setup_expires_at,
            timezone.now() + timedelta(hours=24, minutes=1),
        )

    def test_second_expiry_after_admin_reactivation_deactivates_account_again(self):
        from meetings.password_setup import expire_password_setup_if_due, start_password_setup

        account = User.objects.create_user(
            username="second-expiry-user", password="Neu",
            is_active=True,
        )
        profile = start_password_setup(account)
        profile.password_setup_expires_at = timezone.now() - timedelta(seconds=1)
        profile.save(update_fields=["must_change_password", "password_setup_expires_at"])

        self.assertTrue(expire_password_setup_if_due(account))
        account.refresh_from_db()
        self.assertFalse(account.is_active)

        self.client.force_login(self.admin)
        response = self.client.post(reverse("management_user_edit", args=[account.pk]), {
            "username": account.username, "first_name": "", "last_name": "", "email": "",
            "is_active": "true", "role": "user", "short_description": "",
        })
        self.assertRedirects(response, reverse("management_users"))
        account.refresh_from_db()
        self.assertTrue(account.is_active)
        self.assertTrue(account.check_password("Neu"))
        self.assertTrue(account.meeting_profile.must_change_password)
        self.assertGreater(account.meeting_profile.password_setup_expires_at, timezone.now())

        profile = account.meeting_profile
        profile.password_setup_expires_at = timezone.now() - timedelta(seconds=1)
        profile.save(update_fields=["password_setup_expires_at"])
        self.assertTrue(expire_password_setup_if_due(account))
        account.refresh_from_db()
        self.assertFalse(account.is_active)
