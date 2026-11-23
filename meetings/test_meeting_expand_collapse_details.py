from pathlib import Path
from django.test import SimpleTestCase


class MeetingExpandCollapseDetailsTests(SimpleTestCase):
    def test_feature_is_present_in_template(self):
        template = Path(__file__).resolve().parent.parent / "templates/meetings/meeting.html"
        self.assertIn("meeting-expand-collapse-details", template.read_text(encoding="utf-8"))
