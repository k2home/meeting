from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import EnaioSettings


User = get_user_model()


class EnaioConnectionDiagnosticsTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username="enaio-diagnostics-admin",
            email="admin@example.test",
            password="test-password",
        )

    def test_diagnostics_reports_safe_server_and_configuration_state(self):
        EnaioSettings.objects.create(
            root_folder_id="12345",
            archive_name="Archive",
            register_type_name="Register",
            register_name_field="Name",
            document_type_name="Protocol",
        )
        self.client.force_login(self.admin)

        response = self.client.get(reverse("enaio_connection_diagnostics"))

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["server"]["authenticated_request"])
        self.assertTrue(data["server"]["same_origin_api"])
        self.assertTrue(data["configuration"]["root_folder_configured"])
        self.assertTrue(data["configuration"]["object_definition_configured"])
        self.assertIn("Auslesen der aktiven enaio-Session-GUID", data["checks_not_possible_from_server"])
        self.assertNotIn("root_folder_id", response.content.decode())

    def test_diagnostics_reports_missing_configuration(self):
        self.client.force_login(self.admin)

        response = self.client.get(reverse("enaio_connection_diagnostics"))

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()["configuration"]["root_folder_configured"])
        self.assertFalse(response.json()["configuration"]["object_definition_configured"])

    def test_diagnostics_requires_administrator(self):
        regular_user = User.objects.create_user(
            username="enaio-diagnostics-user",
            password="test-password",
        )
        self.client.force_login(regular_user)

        response = self.client.get(reverse("enaio_connection_diagnostics"))

        self.assertEqual(response.status_code, 403)

    def test_diagnostics_requires_login(self):
        response = self.client.get(reverse("enaio_connection_diagnostics"))

        self.assertEqual(response.status_code, 302)

    def test_diagnostics_is_read_only_get_endpoint(self):
        self.client.force_login(self.admin)

        response = self.client.post(reverse("enaio_connection_diagnostics"))

        self.assertEqual(response.status_code, 405)
