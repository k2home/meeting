from pathlib import Path
from django.test import SimpleTestCase


class SetupPasswordVisibilityTests(SimpleTestCase):
    def test_feature_is_present_in_template(self):
        template = Path(__file__).resolve().parent.parent / "templates/meetings/setup_wizard.html"
        self.assertIn("setup-password-visibility", template.read_text(encoding="utf-8"))
