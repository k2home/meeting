from pathlib import Path
from django.test import SimpleTestCase


class UserGuidePrintTests(SimpleTestCase):
    def test_feature_is_present_in_template(self):
        template = Path(__file__).resolve().parent.parent / "templates/meetings/user_guide.html"
        content = template.read_text(encoding="utf-8")
        self.assertIn('.page-header { display: block !important;', content)
        self.assertIn('break-inside: auto', content)
        self.assertNotIn('.sidebar, .page-header, .guide-index', content)
