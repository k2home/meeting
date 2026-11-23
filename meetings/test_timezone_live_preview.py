from pathlib import Path
from django.test import SimpleTestCase


class TimezoneLivePreviewTests(SimpleTestCase):
    def test_feature_is_present_in_template(self):
        template = Path(__file__).resolve().parent.parent / "templates/meetings/management_settings.html"
        self.assertIn("timezone-live-preview", template.read_text(encoding="utf-8"))
