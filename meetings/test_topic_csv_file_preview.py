from pathlib import Path
from django.test import SimpleTestCase


class TopicCsvFilePreviewTests(SimpleTestCase):
    def test_feature_is_present_in_template(self):
        template = Path(__file__).resolve().parent.parent / "templates/meetings/management_topic_csv_import.html"
        self.assertIn("topic-csv-file-preview", template.read_text(encoding="utf-8"))
