from pathlib import Path
from django.test import SimpleTestCase


class BackupFilePreviewTests(SimpleTestCase):
    def test_feature_is_present_in_template(self):
        template = Path(__file__).resolve().parent.parent / "templates/meetings/management_data.html"
        self.assertIn("backup-file-preview", template.read_text(encoding="utf-8"))
