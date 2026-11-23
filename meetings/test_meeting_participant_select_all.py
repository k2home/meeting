from pathlib import Path
from django.test import SimpleTestCase


class MeetingParticipantSelectAllTests(SimpleTestCase):
    def test_feature_is_present_in_template(self):
        template = Path(__file__).resolve().parent.parent / "templates/meetings/meeting.html"
        content = template.read_text(encoding="utf-8")
        self.assertIn('Teilnehmer ausgewählt.', content)
        self.assertIn('buttons[0].disabled', content)
        self.assertIn('aria-live', content)
