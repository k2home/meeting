from pathlib import Path
from django.test import SimpleTestCase


class TopicCommentAutoresizeTests(SimpleTestCase):
    def test_feature_is_present_in_template(self):
        template = Path(__file__).resolve().parent.parent / "templates/meetings/topic_form.html"
        self.assertIn("topic-comment-autoresize", template.read_text(encoding="utf-8"))
