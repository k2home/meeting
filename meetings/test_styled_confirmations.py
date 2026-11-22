from pathlib import Path
import re

from django.test import SimpleTestCase


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_ROOTS = (
    REPOSITORY_ROOT / "templates",
    REPOSITORY_ROOT / "meetings" / "templates",
)


class StyledConfirmationDialogTests(SimpleTestCase):
    def test_templates_do_not_use_native_browser_confirmation_prompts(self):
        templates = [
            path
            for root in TEMPLATE_ROOTS
            if root.exists()
            for path in root.rglob("*.html")
        ]
        native_confirm = re.compile(r"\bconfirm\s*\(")
        for path in templates:
            with self.subTest(template=path.relative_to(REPOSITORY_ROOT)):
                source = path.read_text(encoding="utf-8")
                self.assertIsNone(native_confirm.search(source))
                self.assertNotIn("data-inline-confirm", source)

    def test_application_and_admin_layouts_provide_the_styled_dialog(self):
        app_base = (REPOSITORY_ROOT / "templates/meetings/base.html").read_text(encoding="utf-8")
        admin_base = (REPOSITORY_ROOT / "templates/admin/base_site.html").read_text(encoding="utf-8")
        for source in (app_base, admin_base):
            self.assertIn('id="app-confirm-dialog"', source)
            self.assertIn('form[data-confirm-message]', source)
            self.assertIn('class="app-confirm-cancel"', source)
            self.assertIn('class="app-confirm-accept"', source)

    def test_destructive_and_finalizing_actions_use_styled_confirmation(self):
        expected = {
            "templates/meetings/meeting.html": "Besprechung wirklich abschließen?",
            "templates/meetings/series_edit.html": "Alle nicht abgeschlossenen Termine dieser Reihe löschen",
            "templates/meetings/series.html": "data-confirm-message=",
            "templates/meetings/topic_form.html": "data-confirm-message=",
            "templates/admin/auth/group/change_list.html": "data-confirm-message=",
        }
        for relative_path, expected_text in expected.items():
            with self.subTest(template=relative_path):
                source = (REPOSITORY_ROOT / relative_path).read_text(encoding="utf-8")
                self.assertIn(expected_text, source)
