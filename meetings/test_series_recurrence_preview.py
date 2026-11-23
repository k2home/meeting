from pathlib import Path
from django.test import SimpleTestCase


class SeriesRecurrencePreviewTests(SimpleTestCase):
    def test_feature_is_present_in_template(self):
        template = Path(__file__).resolve().parent.parent / "templates/meetings/series_edit.html"
        self.assertIn("series-recurrence-preview", template.read_text(encoding="utf-8"))
