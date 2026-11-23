from pathlib import Path
from django.test import SimpleTestCase


class ArchiveLiveSearchTests(SimpleTestCase):
    def test_feature_is_present_in_template(self):
        template = Path(__file__).resolve().parent.parent / "templates/meetings/archive.html"
        self.assertIn("archive-live-search", template.read_text(encoding="utf-8"))
