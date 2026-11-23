from pathlib import Path
from django.test import SimpleTestCase


class MeetingPrintViewTests(SimpleTestCase):
    def test_feature_is_present_in_template(self):
        template = Path(__file__).resolve().parent.parent / "templates/meetings/meeting.html"
        self.assertIn("meeting-print-view", template.read_text(encoding="utf-8"))
