from pathlib import Path
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class DatabaseBackupDownloadHeaderTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username="backup-header-admin",
            email="backup-header-admin@example.test",
            password="test-password",
        )
        self.client.force_login(self.admin)

    @patch("meetings.management_views._record_system_change")
    @patch("meetings.management_views._database_schema_migrations", return_value=[])
    @patch("meetings.management_views._database_client_environment", return_value=({}, "meeting_manager"))
    @patch("meetings.management_views._run_database_client")
    def test_database_backup_download_is_not_cached(
        self,
        run_database_client,
        database_environment,
        schema_migrations,
        record_system_change,
    ):
        def create_dump(command, env, timeout=1800):
            dump_path = Path(command[command.index("--file") + 1])
            dump_path.write_bytes(b"test-postgresql-dump")
            return type("CommandResult", (), {"returncode": 0, "stdout": b"", "stderr": b""})()

        run_database_client.side_effect = create_dump
        response = self.client.get(reverse("management_database_export"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/zip")
        self.assertEqual(response["Cache-Control"], "private, no-store")
        self.assertIn("attachment;", response["Content-Disposition"])
        response.close()
