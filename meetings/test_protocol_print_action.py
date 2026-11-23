from pathlib import Path
from django.test import SimpleTestCase


class ProtocolPrintActionTests(SimpleTestCase):
    def test_feature_is_present_in_template(self):
        template = Path(__file__).resolve().parent.parent / "templates/meetings/protocol.html"
        self.assertIn("protocol-print-action", template.read_text(encoding="utf-8"))
