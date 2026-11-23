from pathlib import Path
from django.test import SimpleTestCase


class OrganizationLogoPreviewTests(SimpleTestCase):
    def test_feature_is_present_in_template(self):
        template = Path(__file__).resolve().parent.parent / "templates/meetings/management_settings.html"
        content = template.read_text(encoding="utf-8")
        self.assertIn("URL.createObjectURL(file)", content)
        self.assertIn("URL.revokeObjectURL", content)
        self.assertIn("preview.onerror", content)
        self.assertIn("preview.dataset.objectUrl === objectUrl", content)
        self.assertIn("delete preview.dataset.objectUrl", content)
