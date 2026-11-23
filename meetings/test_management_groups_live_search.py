from pathlib import Path
from django.test import SimpleTestCase


class ManagementGroupsLiveSearchTests(SimpleTestCase):
    def test_feature_is_present_in_template(self):
        template = Path(__file__).resolve().parent.parent / "templates/meetings/management_groups.html"
        content = template.read_text(encoding="utf-8")
        self.assertIn('form[method="get"] input[name="q"]', content)
        self.assertIn('aria-controls', content)
        self.assertIn('Keine passenden Besprechungsreihen oder Mitglieder gefunden.', content)
        self.assertNotIn('id = "management-group-search"', content)
