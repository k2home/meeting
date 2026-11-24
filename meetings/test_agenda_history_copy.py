from pathlib import Path
from django.test import SimpleTestCase


class AgendaHistoryCopyTests(SimpleTestCase):
    def test_copy_control_is_present(self):
        template = Path(__file__).resolve().parent.parent / "templates/meetings/meeting.html"
        content = template.read_text(encoding="utf-8")
        self.assertIn('window.isSecureContext', content)
        self.assertIn('document.execCommand("copy")', content)
        self.assertIn('button.disabled = true', content)
        self.assertIn('finally', content)
        self.assertIn('previousFocus?.focus?.()', content)
