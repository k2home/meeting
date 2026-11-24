from pathlib import Path

from django.test import SimpleTestCase


class SeriesOverviewLayoutTests(SimpleTestCase):
    def test_compact_overview_keeps_all_series_actions_and_information(self):
        template = Path(__file__).resolve().parent.parent / "templates/meetings/series.html"
        content = template.read_text(encoding="utf-8")
        for expected in (
            "pending_access_requests", "series_delete", "delete_completed",
            "series_extend", "meeting", "meeting_edit", "meeting_delete",
            "other_meetings", "meeting_count", "upcoming_count", "completed_count",
            "new-series-dialog", "id_weekday", "id_start_date",
        ):
            with self.subTest(expected=expected):
                self.assertIn(expected, content)

    def test_series_edit_keeps_recurrence_preview_and_all_maintenance_actions(self):
        template = Path(__file__).resolve().parent.parent / "templates/meetings/series_edit.html"
        content = template.read_text(encoding="utf-8")
        self.assertIn('Intl.DateTimeFormat("de-DE")', content)
        self.assertIn("series_reset_meetings", content)
        self.assertIn("series_extend", content)
        self.assertIn("Intervall", content)
