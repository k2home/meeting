from types import SimpleNamespace
from unittest.mock import patch

from django.test import SimpleTestCase

from .management_views import _validate_backup_migrations


class DatabaseBackupMigrationMetadataTests(SimpleTestCase):
    @patch("meetings.management_views.MigrationLoader")
    def test_accepts_migrations_available_in_current_code(self, migration_loader):
        migration_loader.return_value = SimpleNamespace(
            graph=SimpleNamespace(nodes={("meetings", "0001_initial"), ("meetings", "0002_example")})
        )

        _validate_backup_migrations([
            {"app": "meetings", "name": "0001_initial"},
            {"app": "meetings", "name": "0002_example"},
        ])

    @patch("meetings.management_views.MigrationLoader")
    def test_rejects_backup_from_newer_code_with_unknown_migration(self, migration_loader):
        migration_loader.return_value = SimpleNamespace(
            graph=SimpleNamespace(nodes={("meetings", "0001_initial")})
        )

        with self.assertRaisesRegex(RuntimeError, "neueren oder inkompatiblen"):
            _validate_backup_migrations([
                {"app": "meetings", "name": "0001_initial"},
                {"app": "meetings", "name": "0099_future_change"},
            ])

    @patch("meetings.management_views.MigrationLoader")
    def test_rejects_duplicate_migration_metadata(self, migration_loader):
        migration_loader.return_value = SimpleNamespace(
            graph=SimpleNamespace(nodes={("meetings", "0001_initial")})
        )

        with self.assertRaisesRegex(RuntimeError, "doppelte Einträge"):
            _validate_backup_migrations([
                {"app": "meetings", "name": "0001_initial"},
                {"app": "meetings", "name": "0001_initial"},
            ])

    @patch("meetings.management_views.MigrationLoader")
    def test_rejects_malformed_migration_metadata(self, migration_loader):
        migration_loader.return_value = SimpleNamespace(
            graph=SimpleNamespace(nodes={("meetings", "0001_initial")})
        )

        with self.assertRaisesRegex(RuntimeError, "beschädigt"):
            _validate_backup_migrations([{"app": "meetings"}])
