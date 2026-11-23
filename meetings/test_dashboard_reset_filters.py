from pathlib import Path
from django.test import SimpleTestCase


class DashboardResetFiltersTests(SimpleTestCase):
    def test_feature_is_present_in_template(self):
        template = Path(__file__).resolve().parent.parent / "templates/meetings/dashboard.html"
        content = template.read_text(encoding="utf-8")
        self.assertIn('href="{% url \'dashboard\' %}"', content)
        self.assertIn("Zurücksetzen", content)
        self.assertNotIn("dashboard-reset-filters", content)
