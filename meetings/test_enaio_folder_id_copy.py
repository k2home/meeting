from pathlib import Path
from django.test import SimpleTestCase


class EnaioFolderIdCopyTests(SimpleTestCase):
    def test_feature_is_present_in_template(self):
        template = Path(__file__).resolve().parent.parent / "templates/meetings/management_enaio_settings.html"
        self.assertIn("enaio-folder-id-copy", template.read_text(encoding="utf-8"))
