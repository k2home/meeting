from pathlib import Path
from django.test import SimpleTestCase


class ManagementUserPasswordVisibilityTests(SimpleTestCase):
    def test_feature_is_present_in_template(self):
        template = Path(__file__).resolve().parent.parent / "templates/meetings/management_user_form.html"
        self.assertIn("management-user-password-visibility", template.read_text(encoding="utf-8"))
