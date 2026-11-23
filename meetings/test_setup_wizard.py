import subprocess
from pathlib import Path

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
        response = self.client.post(reverse("setup_wizard"), {
            "username": "firstadmin",
            "first_name": "Erste",
            "last_name": "Administration",
            "email": "admin@example.org",
            "password1": "StrongSetupPassword1!",
            "password2": "StrongSetupPassword1!",
        })
        self.assertRedirects(response, "/setup/?step=organization")
        user = User.objects.get(username="firstadmin")
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.groups.filter(name="Admin").exists())
        self.assertEqual(int(self.client.session["initial_setup_user_id"]), user.pk)

    def test_first_administrator_form_does_not_require_activation_code(self):
        response = self.client.get(reverse("setup_wizard"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Einrichtungscode")

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

    def test_system_check_and_completion_steps(self):
        user = User.objects.create_superuser(username="root", email="root@example.org", password="StrongPassword123!")
        self.client.force_login(user)
        session = self.client.session
        session["initial_setup_user_id"] = user.pk
        session["initial_setup_organization_saved"] = True
        session.save()
        checks = [{"label": "Testprüfung", "ok": True, "detail": "OK"}]
        with patch("meetings.setup_views._setup_checks", return_value=checks):
            response = self.client.get("/setup/?step=system")
            self.assertEqual(response.status_code, 200)
            response = self.client.post("/setup/?step=system")
            self.assertRedirects(response, "/setup/?step=complete")
            response = self.client.post("/setup/?step=complete")
        self.assertRedirects(response, reverse("dashboard"))
        self.assertNotIn("initial_setup_user_id", self.client.session)

    def test_installation_scripts_have_valid_bash_syntax(self):
        root = Path(__file__).resolve().parent.parent
        for script in ("deploy/install-debian.sh", "deploy/install-docker.sh"):
            with self.subTest(script=script):
                result = subprocess.run(["bash", "-n", str(root / script)], capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
