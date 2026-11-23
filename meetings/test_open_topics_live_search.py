from pathlib import Path
from django.test import SimpleTestCase


class OpenTopicsLiveSearchTests(SimpleTestCase):
    def test_feature_is_present_in_template(self):
        template = Path(__file__).resolve().parent.parent / "templates/meetings/open_topics.html"
        content = template.read_text(encoding="utf-8")
        self.assertIn('class="card open-topic-card"', content)
        self.assertIn('querySelectorAll(".open-topic-card")', content)
        self.assertIn('aria-live', content)
        self.assertNotIn('querySelectorAll("section.card")', content)
