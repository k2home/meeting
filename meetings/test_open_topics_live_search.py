from pathlib import Path
from django.test import SimpleTestCase


class OpenTopicsLiveSearchTests(SimpleTestCase):
    def test_feature_is_present_in_template(self):
        template = Path(__file__).resolve().parent.parent / "templates/meetings/open_topics.html"
        self.assertIn("open-topics-live-search", template.read_text(encoding="utf-8"))
