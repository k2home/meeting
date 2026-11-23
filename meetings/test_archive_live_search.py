from pathlib import Path
from django.test import SimpleTestCase


class ArchiveLiveSearchTests(SimpleTestCase):
    def test_feature_is_present_in_template(self):
        template = Path(__file__).resolve().parent.parent / "templates/meetings/archive.html"
        content = template.read_text(encoding="utf-8")
        self.assertIn('querySelectorAll(".archive-search-group")', content)
        self.assertIn('aria-controls', content)
        self.assertIn('aria-live', content)
        self.assertNotIn('querySelectorAll("section.card")', content)
