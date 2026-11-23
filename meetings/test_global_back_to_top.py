from pathlib import Path
from django.test import SimpleTestCase


class GlobalBackToTopTests(SimpleTestCase):
    def test_feature_is_present_in_template(self):
        template = Path(__file__).resolve().parent.parent / "templates/meetings/base.html"
        self.assertIn("global-back-to-top", template.read_text(encoding="utf-8"))
