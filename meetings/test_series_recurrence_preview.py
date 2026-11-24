from pathlib import Path

from django.test import SimpleTestCase


class SeriesRecurrencePreviewTests(SimpleTestCase):
    def test_feature_is_present_in_template(self):
        template = Path(__file__).resolve().parent.parent / "templates/meetings/series_edit.html"
        content = template.read_text(encoding="utf-8")
        self.assertIn('Intl.DateTimeFormat("de-DE")', content)
        self.assertIn('formatDate(startValue)', content)
        self.assertIn('Intervall', content)
