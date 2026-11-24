from unittest.mock import patch

from django.test import SimpleTestCase

from .setup_views import _setup_checks


class SetupDiagnosticDisclosureTests(SimpleTestCase):
    @patch("meetings.setup_views.call_command", side_effect=RuntimeError("SECRET_DJANGO_SETTING"))
    @patch("meetings.setup_views.MigrationExecutor", side_effect=RuntimeError("SECRET_MIGRATION_DETAIL"))
    @patch("meetings.setup_views.connection.ensure_connection", side_effect=RuntimeError(
        "postgres://private-user:private-password@private-db:5432/meeting_manager"
    ))
    def test_internal_exception_details_are_not_shown_to_setup_user(
        self,
        ensure_connection,
        migration_executor,
        call_command,
    ):
        checks = _setup_checks()
        details = " ".join(check["detail"] for check in checks)

        self.assertNotIn("private-user", details)
        self.assertNotIn("private-password", details)
        self.assertNotIn("private-db", details)
        self.assertNotIn("SECRET_MIGRATION_DETAIL", details)
        self.assertNotIn("SECRET_DJANGO_SETTING", details)
        self.assertIn("Serverprotokolle prüfen", details)
