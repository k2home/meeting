from pathlib import Path

from django.test import SimpleTestCase


ROOT = Path(__file__).resolve().parent.parent


class LoginRateLimitConfigurationTests(SimpleTestCase):
    def test_docker_nginx_throttles_login_by_source_ip(self):
        config = (ROOT / "docker" / "nginx.conf").read_text(encoding="utf-8")
        self.assertIn("limit_req_zone $binary_remote_addr zone=meeting_login_limit:10m rate=10r/m;", config)
        self.assertIn("location = /login/", config)
        self.assertIn("limit_req zone=meeting_login_limit burst=10 nodelay;", config)
        self.assertIn("limit_req_status 429;", config)

    def test_debian_nginx_throttles_login_by_source_ip(self):
        config = (ROOT / "deploy" / "nginx-meeting-manager.conf").read_text(encoding="utf-8")
        self.assertIn("limit_req_zone $binary_remote_addr zone=meeting_login_limit:10m rate=10r/m;", config)
        self.assertIn("location = /login/", config)
        self.assertIn("limit_req zone=meeting_login_limit burst=10 nodelay;", config)
        self.assertIn("limit_req_status 429;", config)
