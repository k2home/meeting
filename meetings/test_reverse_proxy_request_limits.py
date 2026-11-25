from pathlib import Path

from django.test import SimpleTestCase


ROOT = Path(__file__).resolve().parent.parent


class ReverseProxyRequestLimitTests(SimpleTestCase):
    def test_docker_nginx_limits_general_requests_and_allows_large_backup_imports(self):
        config = (ROOT / "docker" / "nginx.conf").read_text(encoding="utf-8")
        self.assertIn("client_max_body_size 32m;", config)
        self.assertIn("location = /verwaltung/daten/vollbackup/import/", config)
        self.assertIn("client_max_body_size 1g;", config)

    def test_debian_nginx_limits_general_requests_and_allows_large_backup_imports(self):
        config = (ROOT / "deploy" / "nginx-meeting-manager.conf").read_text(encoding="utf-8")
        self.assertIn("client_max_body_size 32m;", config)
        self.assertIn("location = /verwaltung/daten/vollbackup/import/", config)
        self.assertIn("client_max_body_size 1g;", config)
