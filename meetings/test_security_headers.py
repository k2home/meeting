from django.test import TestCase
from django.urls import reverse


class ContentSecurityPolicyTests(TestCase):
    def test_application_responses_include_same_origin_csp_baseline(self):
        response = self.client.get(reverse("login"))

        self.assertIn("Content-Security-Policy", response)
        policy = response["Content-Security-Policy"]
        self.assertIn("default-src 'self'", policy)
        self.assertIn("object-src 'none'", policy)
        self.assertIn("base-uri 'self'", policy)
        self.assertIn("frame-ancestors 'none'", policy)
        self.assertIn("form-action 'self'", policy)

    def test_inline_script_compatibility_is_explicitly_limited_to_same_origin_pages(self):
        response = self.client.get(reverse("login"))
        policy = response["Content-Security-Policy"]

        # Current templates still contain inline scripts. Keep that compatibility
        # explicit rather than silently permitting arbitrary external script hosts.
        self.assertIn("script-src 'self' 'unsafe-inline'", policy)
        self.assertNotIn("https:", policy)
