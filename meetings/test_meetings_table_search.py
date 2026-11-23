from pathlib import Path
from django.test import SimpleTestCase


class MeetingsTableSearchTests(SimpleTestCase):
    def test_feature_is_present_in_template(self):
        template = Path(__file__).resolve().parent.parent / "templates/meetings/meetings_overview.html"
        content = template.read_text(encoding="utf-8")
        self.assertIn('querySelector(".meetings-series-table")', content)
        self.assertIn('setAttribute("aria-label"', content)
        self.assertNotIn('querySelectorAll(".card")', content)
