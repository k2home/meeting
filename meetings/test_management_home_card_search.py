from pathlib import Path
from django.test import SimpleTestCase


class ManagementHomeCardSearchTests(SimpleTestCase):
    def test_feature_is_present_in_template(self):
        template = Path(__file__).resolve().parent.parent / "templates/meetings/management.html"
        self.assertIn("management-home-card-search", template.read_text(encoding="utf-8"))
