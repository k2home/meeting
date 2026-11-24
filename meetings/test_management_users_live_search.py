from pathlib import Path

from django.test import SimpleTestCase


class ManagementUsersLiveSearchTests(SimpleTestCase):
    def test_live_search_is_accessible_and_reports_no_matches(self):
        template = (
            Path(__file__).resolve().parent.parent
            / "templates/meetings/management_users.html"
        )
        content = template.read_text(encoding="utf-8")

        self.assertIn('input.setAttribute("aria-controls", table.id)', content)
        self.assertIn('feedback.setAttribute("aria-live", "polite")', content)
        self.assertIn("Keine passenden Nutzer gefunden.", content)

    def test_live_search_only_uses_name_username_and_email_cells(self):
        template = (
            Path(__file__).resolve().parent.parent
            / "templates/meetings/management_users.html"
        )
        content = template.read_text(encoding="utf-8")

        self.assertIn(
            ".map(index => row.cells[index]?.textContent || \"\")",
            content,
        )
        self.assertIn("[0, 1, 2]", content)
        self.assertNotIn("row.textContent", content)
