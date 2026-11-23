from pathlib import Path
from django.test import SimpleTestCase


class ManagementUsersLiveSearchTests(SimpleTestCase):
    def test_feature_is_present_in_template(self):
        template = Path(__file__).resolve().parent.parent / "templates/meetings/management_users.html"
        content = template.read_text(encoding="utf-8")
        self.assertIn('aria-controls', content)
        self.assertIn('Keine passenden Nutzer gefunden.', content)
        self.assertIn('aria-live', content)
