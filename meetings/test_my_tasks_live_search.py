from pathlib import Path

from django.test import SimpleTestCase


class MyTasksLiveSearchTests(SimpleTestCase):
    def test_feature_is_present_in_template(self):
        template = Path(__file__).resolve().parent.parent / "templates/meetings/my_tasks.html"
        content = template.read_text(encoding="utf-8")
        self.assertIn('id="my-tasks-search"', content)
        self.assertIn('aria-controls="my-tasks-table-0 my-tasks-table-1"', content)
        self.assertIn('Keine passenden Aufgaben gefunden.', content)
        self.assertIn('aria-live="polite"', content)
