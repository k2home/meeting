from pathlib import Path
from django.test import SimpleTestCase


class MeetingDateValidationTests(SimpleTestCase):
    def test_feature_is_present_in_template(self):
        template = Path(__file__).resolve().parent.parent / "templates/meetings/meeting_date_form.html"
        self.assertIn("meeting-date-validation", template.read_text(encoding="utf-8"))
