from pathlib import Path
from django.test import SimpleTestCase


class MeetingPrintViewTests(SimpleTestCase):
    def test_feature_is_present_in_template(self):
        template = Path(__file__).resolve().parent.parent / "templates/meetings/meeting.html"
        content = template.read_text(encoding="utf-8")
        self.assertIn('.page-header { display: block !important;', content)
        self.assertNotIn('.sidebar, .page-header, .no-print', content)
        self.assertIn('break-inside: auto', content)
