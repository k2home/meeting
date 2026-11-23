from pathlib import Path
from django.test import SimpleTestCase


class MeetingsTableSearchTests(SimpleTestCase):
    def test_feature_is_present_in_template(self):
        template = Path(__file__).resolve().parent.parent / "templates/meetings/meetings_overview.html"
        self.assertIn("meetings-table-search", template.read_text(encoding="utf-8"))
