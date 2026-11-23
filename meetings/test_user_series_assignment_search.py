from pathlib import Path
from django.test import SimpleTestCase


class UserSeriesAssignmentSearchTests(SimpleTestCase):
    def test_feature_is_present_in_template(self):
        template = Path(__file__).resolve().parent.parent / "templates/meetings/management_user_series.html"
        self.assertIn("user-series-assignment-search", template.read_text(encoding="utf-8"))
