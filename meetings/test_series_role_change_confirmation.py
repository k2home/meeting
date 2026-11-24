from pathlib import Path
from django.test import SimpleTestCase


class SeriesRoleChangeConfirmationTests(SimpleTestCase):
    def test_feature_is_present_in_template(self):
        template = Path(__file__).resolve().parent.parent / "templates/meetings/user_overview.html"
        content = template.read_text(encoding="utf-8")
        self.assertIn('select.dataset.currentRole', content)
        self.assertIn('data-confirm-message=', content)
        self.assertNotIn('window.confirm(', content)
