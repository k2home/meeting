import os
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import OrganizationSettings

User = get_user_model()


class InitialSetupWizardTests(TestCase):
    def test_first_visit_redirects_login_to_setup_when_no_users_exist(self):
        response = self.client.get(reverse("login"))
        self.assertRedirects(response, reverse("setup_wizard"))

    def test_first_administrator_is_created_and_logged_in(self):
        with patch.dict(os.environ, {"SETUP_TOKEN": "test-setup-token"}):
            response = self.client.post(reverse("setup_wizard"), {
            "username": "firstadmin",
            "first_name": "Erste",
            "last_name": "Administration",
            "email": "admin@example.org",
            "setup_token": "test-setup-token",
            "password1": "StrongSetupPassword1!",
            "password2": "StrongSetupPassword1!",
            })
        self.assertRedirects(response, "/setup/?step=organization")
        user = User.objects.get(username="firstadmin")
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.groups.filter(name="Admin").exists())
        self.assertEqual(int(self.client.session["initial_setup_user_id"]), user.pk)

    def test_first_administrator_requires_valid_setup_token(self):
        response = self.client.post(reverse("setup_wizard"), {
            "username": "attacker", "first_name": "Bad", "last_name": "Actor",
            "email": "bad@example.org", "setup_token": "wrong",
            "password1": "StrongSetupPassword1!", "password2": "StrongSetupPassword1!",
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.exists())

    def test_setup_account_creation_is_disabled_after_first_user_exists(self):
        User.objects.create_user(username="existing", password="StrongPassword123!")
        response = self.client.get(reverse("setup_wizard"))
        self.assertRedirects(response, reverse("login"))

    def test_organization_step_requires_setup_session(self):
        User.objects.create_superuser(username="root", email="root@example.org", password="StrongPassword123!")
        response = self.client.get(reverse("setup_wizard"), {"step": "organization"})
        self.assertRedirects(response, reverse("login"))

    def test_organization_step_saves_existing_organization_settings(self):
        user = User.objects.create_superuser(username="root", email="root@example.org", password="StrongPassword123!")
        self.client.force_login(user)
        session = self.client.session
        session["initial_setup_user_id"] = user.pk
        session.save()
        response = self.client.post("/setup/?step=organization", {
            "name": "Fachbereich 20", "short_name": "FB20", "timezone": "Europe/Berlin",
            "attachment_max_size_mb": "20", "primary_color": "#00549F",
            "primary_color_light": "", "primary_color_dark": "",
            "secondary_color": "#8FC5FF", "secondary_color_light": "", "secondary_color_dark": "",
            "tertiary_color": "#FFCC00", "tertiary_color_light": "", "tertiary_color_dark": "",
        })
        self.assertRedirects(response, "/setup/?step=system")
        settings_obj = OrganizationSettings.objects.get(pk=1)
        self.assertEqual(settings_obj.name, "Fachbereich 20")
        self.assertEqual(settings_obj.short_name, "FB20")

    def test_existing_users_cannot_reenter_setup_wizard_without_setup_session(self):
        user = User.objects.create_superuser(username="root", email="root@example.org", password="StrongPassword123!")
        self.client.force_login(user)
        response = self.client.get(reverse("setup_wizard"), {"step": "organization"})
        self.assertRedirects(response, reverse("dashboard"))
