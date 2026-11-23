from pathlib import Path
from django.test import SimpleTestCase


class DashboardSearchShortcutTests(SimpleTestCase):
    def test_feature_is_present_in_template(self):
        template = Path(__file__).resolve().parent.parent / "templates/meetings/dashboard.html"
        self.assertIn("dashboard-search-shortcut", template.read_text(encoding="utf-8"))
