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
        include = '{% include "meetings/includes/confirmation_dialog.html" %}'
        self.assertIn(include, app_base)
        self.assertIn(include, admin_base)
        shared = (REPOSITORY_ROOT / "templates/meetings/includes/confirmation_dialog.html").read_text(encoding="utf-8")
        self.assertIn('id="app-confirm-dialog"', shared)
        self.assertIn('form[data-confirm-message]', shared)
        self.assertIn('class="app-confirm-cancel"', shared)
        self.assertIn('class="app-confirm-accept"', shared)
        self.assertEqual(app_base.count('id="app-confirm-dialog"'), 0)
        self.assertEqual(admin_base.count('id="app-confirm-dialog"'), 0)

    def test_destructive_and_finalizing_actions_use_styled_confirmation(self):
        expected = {
            "templates/meetings/meeting.html": "Besprechung wirklich abschließen?",
            "templates/meetings/series_edit.html": "Alle nicht abgeschlossenen Termine dieser Reihe löschen",
            "templates/meetings/series.html": "Die Terminreihe „{{ s.name }}“ bis zum 31.12. des Folgejahres verlängern?",
            "templates/meetings/topic_form.html": "Thema „{{ topic.title }}“ in die ausgewählte Besprechungsreihe übertragen?",
            "templates/admin/auth/group/change_list.html": "data-confirm-message=",
        }
        expected["templates/meetings/meeting.html"] = "Der aktuelle Protokoll-Snapshot wird aus der aktiven Ansicht entfernt"
        for relative_path, expected_text in expected.items():
            with self.subTest(template=relative_path):
                source = (REPOSITORY_ROOT / relative_path).read_text(encoding="utf-8")
                self.assertIn(expected_text, source)
        meeting_source = (REPOSITORY_ROOT / "templates/meetings/meeting.html").read_text(encoding="utf-8")
        self.assertIn("Besprechung wirklich abschließen?", meeting_source)

    def test_confirmation_buttons_use_theme_aware_accessible_colors(self):
        shared = (REPOSITORY_ROOT / "templates/meetings/includes/confirmation_dialog.html").read_text(encoding="utf-8")
        self.assertIn("background:var(--primary-button-bg", shared)
        self.assertIn("color:var(--primary-button-text,#fff)", shared)
        self.assertIn("background:var(--soft-bg,var(--admin-surface,#e9edf2))", shared)
        self.assertIn("color:var(--text,var(--admin-text,#344054))", shared)
