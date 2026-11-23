from pathlib import Path
from django.test import SimpleTestCase


class PasswordResetVisibilityTests(SimpleTestCase):
    def test_feature_is_present_in_template(self):
        template = Path(__file__).resolve().parent.parent / "templates/meetings/password_reset_confirm.html"
        self.assertIn("password-reset-visibility", template.read_text(encoding="utf-8"))
