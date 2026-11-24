from pathlib import Path
from django.test import SimpleTestCase


class AttachmentFilePreviewTests(SimpleTestCase):
    def test_feature_is_present_in_template(self):
        template = Path(__file__).resolve().parent.parent / "templates/meetings/attachment_form.html"
        self.assertIn("attachment-file-preview", template.read_text(encoding="utf-8"))
