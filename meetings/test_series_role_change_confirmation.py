from pathlib import Path
from django.test import SimpleTestCase


class SeriesRoleChangeConfirmationTests(SimpleTestCase):
    def test_feature_is_present_in_template(self):
        template = Path(__file__).resolve().parent.parent / "templates/meetings/user_overview.html"
        self.assertIn("series-role-change-confirmation", template.read_text(encoding="utf-8"))
