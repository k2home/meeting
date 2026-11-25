from unittest.mock import patch
import subprocess
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import AuditEvent, OrganizationSettings

User = get_user_model()


@override_settings(SETUP_TOKEN_REQUIRED=False)
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

    def test_setup_requires_valid_activation_token_by_default(self):
        with override_settings(SETUP_TOKEN_REQUIRED=True, SETUP_TOKEN="test-activation-token"):
            response = self.client.get(reverse("setup_wizard"))
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, "Aktivierungstoken")
            response = self.client.post(reverse("setup_wizard"), {"setup_token": "wrong-token"})
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, "ungültig")
            self.assertFalse(User.objects.exists())
            response = self.client.post(reverse("setup_wizard"), {"setup_token": "test-activation-token"})
            self.assertRedirects(response, "/setup/?step=account")
            response = self.client.get("/setup/?step=account")
            self.assertContains(response, "Administratorkonto anlegen")

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
            "name": "Fachbereich 20", "short_name": "FB20", "timezone": "Europe/Berlin", "start_password": "Neu",
            "attachment_max_size_mb": "20", "primary_color": "#002D72",
            "secondary_color": "#0072CE", "tertiary_color": "#FFCD00",
        })
        self.assertRedirects(response, "/setup/?step=system")
        settings_obj = OrganizationSettings.objects.get(pk=1)
        self.assertEqual(settings_obj.name, "Fachbereich 20")
        self.assertEqual(settings_obj.short_name, "FB20")
        self.assertEqual(settings_obj.primary_color, "#002D72")
        self.assertEqual(settings_obj.secondary_color, "#0072CE")
        self.assertEqual(settings_obj.tertiary_color, "#FFCD00")
        self.assertEqual(settings_obj.primary_color_light, "")
        self.assertEqual(settings_obj.primary_color_dark, "")
        setup_event = AuditEvent.objects.get(summary="Organisationseinstellungen bei der Ersteinrichtung gespeichert")
        self.assertNotIn("Neu", str(setup_event.changes))
        self.assertEqual(setup_event.changes["Startpasswort"]["nachher"], "Geändert")

    @patch("cairosvg.svg2png", side_effect=ValueError("invalid SVG"))
    def test_invalid_setup_svg_does_not_persist_partial_organization_settings(self, _convert):
        user = User.objects.create_superuser(username="root-svg", email="root-svg@example.org", password="StrongSetupPassword1!")
        self.client.force_login(user)
        session = self.client.session
        session["initial_setup_user_id"] = user.pk
        session.save()

        response = self.client.post("/setup/?step=organization", {
            "name": "Nicht speichern",
            "short_name": "NS",
            "timezone": "Europe/Berlin",
            "start_password": "Nicht-im-Audit",
            "attachment_max_size_mb": "20",
            "primary_color": "#002D72",
            "secondary_color": "#0072CE",
            "tertiary_color": "#FFCD00",
            "logo": SimpleUploadedFile("invalid.svg", b"<svg>ungueltig", content_type="image/svg+xml"),
        })

        self.assertEqual(response.status_code, 200)
        self.assertFalse(OrganizationSettings.objects.filter(pk=1).exists())
        self.assertContains(response, "Das Logo konnte nicht verarbeitet werden")

    def test_setup_organization_form_shows_only_three_base_colors_with_defaults(self):
        user = User.objects.create_superuser(username="root", email="root@example.org", password="StrongPassword123!")
        self.client.force_login(user)
        session = self.client.session
        session["initial_setup_user_id"] = user.pk
        session.save()
        response = self.client.get("/setup/?step=organization")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'value="#002D72"')
        self.assertContains(response, 'value="#0072CE"')
        self.assertContains(response, 'value="#FFCD00"')
        self.assertNotContains(response, "Primärfarbe – Hellmodus")
        self.assertNotContains(response, "Primärfarbe – Dunkelmodus")

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
