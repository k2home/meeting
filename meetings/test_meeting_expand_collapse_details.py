from pathlib import Path
from django.test import SimpleTestCase


class MeetingExpandCollapseDetailsTests(SimpleTestCase):
    def test_feature_is_present_in_template(self):
        template = Path(__file__).resolve().parent.parent / "templates/meetings/meeting.html"
        content = template.read_text(encoding="utf-8")
        self.assertIn('addEventListener("toggle", updateButton)', content)
        self.assertIn('setAttribute("aria-pressed"', content)
        self.assertIn('details.every(item => item.open)', content)
