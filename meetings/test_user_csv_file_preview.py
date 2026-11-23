from pathlib import Path
from django.test import SimpleTestCase


class UserCsvFilePreviewTests(SimpleTestCase):
    def test_feature_is_present_in_template(self):
        template = Path(__file__).resolve().parent.parent / "templates/meetings/management_user_csv_import.html"
        self.assertIn("user-csv-file-preview", template.read_text(encoding="utf-8"))
