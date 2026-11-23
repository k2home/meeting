from pathlib import Path
from django.test import SimpleTestCase


class TopicTitleCharacterCounterTests(SimpleTestCase):
    def test_feature_is_present_in_template(self):
        template = Path(__file__).resolve().parent.parent / "templates/meetings/topic_form.html"
        content = template.read_text(encoding="utf-8")
        self.assertIn('field.setAttribute(', content)
        self.assertIn('counter.id', content)
        self.assertIn('aria-live", "off"', content)
