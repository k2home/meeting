from pathlib import Path
from django.test import SimpleTestCase


class MyTasksLiveSearchTests(SimpleTestCase):
    def test_feature_is_present_in_template(self):
        template = Path(__file__).resolve().parent.parent / "templates/meetings/my_tasks.html"
        self.assertIn("my-tasks-live-search", template.read_text(encoding="utf-8"))
