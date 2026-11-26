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
        self.assertIn("[0, 1, 2, 3]", content)
        self.assertNotIn("row.textContent", content)


class ManagementUsersSortingTests(SimpleTestCase):
    def test_user_table_has_accessible_sort_controls_for_all_data_columns(self):
        template = (
            Path(__file__).resolve().parent.parent
            / "templates/meetings/management_users.html"
        )
        content = template.read_text(encoding="utf-8")

        for column in range(7):
            self.assertIn(f'data-sort-column="{column}"', content)
        self.assertIn('aria-sort="none"', content)
        self.assertIn('aria-label="Nach letzter Anmeldung sortieren"', content)
        self.assertIn('aria-label="Nach Erstellungsdatum sortieren"', content)

    def test_sorting_uses_german_numeric_collation_and_timestamp_values(self):
        template = (
            Path(__file__).resolve().parent.parent
            / "templates/meetings/management_users.html"
        )
        content = template.read_text(encoding="utf-8")

        self.assertIn('new Intl.Collator("de", { numeric: true, sensitivity: "base" })', content)
        self.assertIn('data-sort-value="{{ item.account.last_login|date:\'U\' }}"', content)
        self.assertIn('data-sort-value="{{ item.account.date_joined|date:\'U\' }}"', content)
        self.assertIn('header?.setAttribute("aria-sort"', content)
