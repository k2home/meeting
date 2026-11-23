from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import EnaioSettings, EnaioDiagnosticReport, EnaioAgent, EnaioAgentLog


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
        # The object definition is deliberately no longer configured manually.
        # Automatic retrieval from the running enaio client is planned, not implemented yet.
        self.assertFalse(data["configuration"]["object_definition_configured"])
        self.assertTrue(data["configuration"]["object_definition_automatic"])
        self.assertEqual(data["configuration"]["missing_fields"], [])
        self.assertIn("Auslesen der aktiven enaio-Session-GUID", data["checks_not_possible_from_server"])
        self.assertNotIn("root_folder_id", response.content.decode())

    def test_diagnostics_reports_missing_configuration(self):
        self.client.force_login(self.admin)

        response = self.client.get(reverse("enaio_connection_diagnostics"))

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()["configuration"]["root_folder_configured"])
        data = response.json()["configuration"]
        self.assertFalse(data["object_definition_configured"])
        self.assertTrue(data["object_definition_automatic"])
        self.assertEqual(
            {item["field"] for item in data["missing_fields"]},
            {"document_type_name"},
        )

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



class EnaioSharedDiagnosticReportTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username="enaio-report-admin", email="report-admin@example.test", password="test-password"
        )
        self.client.force_login(self.admin)

    def test_report_is_saved_analyzed_and_available_to_another_request(self):
        payload = {
            "report_type": "Meeting Manager – enaio Browserdiagnose",
            "generated_at": "2026-11-23T20:22:56.314Z",
            "browser": [{"test": "COM", "result": "NICHT DIREKT VERFÜGBAR", "detail": "Edge"}],
            "server": [{"test": "Objektdefinition", "result": "UNVOLLSTÄNDIG", "detail": "Feld fehlt"}],
            "conclusion": [],
            "credential": "Bearer top-secret-value",
        }
        response = self.client.post(
            reverse("enaio_diagnostic_report_save"),
            data=__import__("json").dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        saved = response.json()
        self.assertEqual(saved["analysis"]["diagnostic_warnings"], 2)
        self.assertNotIn("top-secret-value", response.content.decode())
        self.assertEqual(EnaioDiagnosticReport.objects.count(), 1)

        latest = self.client.get(reverse("enaio_diagnostic_report_latest"))
        self.assertEqual(latest.status_code, 200)
        self.assertTrue(latest.json()["available"])
        self.assertEqual(latest.json()["id"], saved["id"])

    def test_saved_report_includes_existing_redacted_agent_logs(self):
        agent = EnaioAgent.objects.create(user=self.admin, device_name="Test-PC")
        EnaioAgentLog.objects.create(agent=agent, level="ERROR", message="token=agent-secret failed")
        payload = {"report_type": "Meeting Manager – enaio Browserdiagnose", "browser": [], "server": [], "conclusion": []}
        response = self.client.post(
            reverse("enaio_diagnostic_report_save"),
            data=__import__("json").dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        body = response.content.decode()
        self.assertNotIn("agent-secret", body)
        self.assertIn("[REDACTED]", body)
        self.assertEqual(response.json()["analysis"]["agent_errors"], 1)

    def test_only_admin_can_save_or_read_reports(self):
        user = User.objects.create_user(username="enaio-report-user", password="test-password")
        self.client.force_login(user)
        payload = {"report_type": "Meeting Manager – enaio Browserdiagnose"}
        denied_save = self.client.post(
            reverse("enaio_diagnostic_report_save"),
            data=__import__("json").dumps(payload),
            content_type="application/json",
        )
        denied_read = self.client.get(reverse("enaio_diagnostic_report_latest"))
        self.assertEqual(denied_save.status_code, 403)
        self.assertEqual(denied_read.status_code, 403)


    def test_uploaded_local_log_is_analyzed_and_redacted(self):
        payload = {
            "report_type": "Meeting Manager – enaio Browserdiagnose",
            "browser": [], "server": [], "conclusion": [],
            "local_log_file": "agent.log",
            "local_log_text": "2026-11-23 ERROR COM activation failed token=local-secret\\n2026-11-23 WARNING retry",
        }
        response = self.client.post(
            reverse("enaio_diagnostic_report_save"),
            data=__import__("json").dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["analysis"]["local_log_errors"], 1)
        self.assertEqual(data["analysis"]["local_log_warnings"], 1)
        self.assertNotIn("local-secret", response.content.decode())
