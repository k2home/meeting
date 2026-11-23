from pathlib import Path
from django.test import SimpleTestCase


class EnaioFolderIdCopyTests(SimpleTestCase):
    def test_feature_is_present_in_template(self):
        template = Path(__file__).resolve().parent.parent / "templates/meetings/management_enaio_settings.html"
        content = template.read_text(encoding="utf-8")
        self.assertIn("window.isSecureContext", content)
        self.assertIn('document.execCommand("copy")', content)
        self.assertIn("button.disabled = true", content)
