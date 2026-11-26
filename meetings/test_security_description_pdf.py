from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from unittest.mock import patch


class SecurityDescriptionPdfTests(TestCase):
    def test_pdf_requires_authentication(self):
        response = self.client.get(reverse("security_description_pdf"))
        self.assertEqual(response.status_code, 302)

    def test_authenticated_user_can_download_pdf(self):
        user = get_user_model().objects.create_user(
            username="security-doc-reader", password="Strong-test-password-123!"
        )
        self.client.force_login(user)

        response = self.client.get(reverse("security_description_pdf"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")
        self.assertIn("attachment;", response["Content-Disposition"])
        self.assertEqual(response["Cache-Control"], "private, no-store")
        self.assertTrue(response.content.startswith(b"%PDF-"))
        self.assertGreater(len(response.content), 10_000)


class SecurityDescriptionPageTests(TestCase):
    def test_security_review_page_requires_authentication(self):
        response = self.client.get(reverse("security_description"))
        self.assertEqual(response.status_code, 302)

    def test_authenticated_user_sees_full_review_and_pdf_link(self):
        user = get_user_model().objects.create_user(
            username="security-review-reader", password="Strong-test-password-123!"
        )
        self.client.force_login(user)

        response = self.client.get(reverse("security_description"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Rollen- und Berechtigungskonzept")
        self.assertContains(response, "Konkrete Maßnahmen und empfohlene Vorgehensweisen")
        self.assertContains(response, reverse("security_description_pdf"))
        self.assertContains(response, "Inhaltsverzeichnis")
        self.assertContains(response, 'href="#1-kurzbeschreibung-und-zweck"')
        self.assertContains(response, 'class="toc"')

    @patch("meetings.views._debian_testing_mode_enabled", return_value=True)
    def test_review_marking_tools_are_only_rendered_in_testing_mode(self, _testing_mode):
        user = get_user_model().objects.create_user(
            username="security-review-marker", password="Strong-test-password-123!"
        )
        self.client.force_login(user)

        response = self.client.get(reverse("security_description"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Taste <kbd>M</kbd>")
        self.assertNotContains(response, 'id="add-review-mark"')
        self.assertContains(response, 'event.key.toLowerCase() !== "m"')
        self.assertContains(response, 'id="export-review-marks"')
        self.assertContains(response, "localStorage")
        self.assertContains(response, "Prüfmarkierungen")


class TestDocumentationPageTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="test-documentation-reader", password="Strong-test-password-123!"
        )
        self.client.force_login(self.user)

    def test_test_documentation_requires_authentication(self):
        self.client.logout()
        response = self.client.get(reverse("test_documentation"))
        self.assertEqual(response.status_code, 302)

    @patch("meetings.guide_views._test_documentation_testing_mode_enabled", return_value=False)
    def test_checklist_is_read_only_outside_testing_mode(self, _testing_mode):
        response = self.client.get(reverse("test_documentation"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Prüfung des Verfahrens")
        self.assertContains(response, 'type="checkbox"')
        self.assertContains(response, "Test erfolgreich")
        self.assertContains(response, "Lesemodus")
        self.assertContains(response, "disabled")
        self.assertNotContains(response, 'id="download-test-documentation"')
        self.assertNotContains(response, 'id="test-documentation-markdown-source"')
        self.assertNotContains(response, "test_documentation_toggle")

    @patch("meetings.guide_views._test_documentation_testing_mode_enabled", return_value=True)
    def test_testing_mode_enables_editing_and_markdown_download(self, _testing_mode):
        response = self.client.get(reverse("test_documentation"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "TESTING-Modus ist aktiv")
        self.assertContains(response, 'id="download-test-documentation"')
        self.assertContains(response, 'id="test-documentation-markdown-source"')
        self.assertContains(response, "text/markdown;charset=utf-8")
        self.assertContains(response, "Pruefung-des-Verfahrens-Testdokumentation-")
        self.assertNotContains(response, "data-save-url")
        self.assertNotContains(response, "test_documentation_toggle")

    def test_user_guide_links_to_test_documentation(self):
        response = self.client.get(reverse("user_guide"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse("test_documentation"))
        self.assertContains(response, "Prüfung des Verfahrens – Testcheckliste")

    def test_markdown_checkbox_rendering_respects_existing_status_and_edit_mode(self):
        from meetings.guide_views import _render_test_documentation_markers

        source = "- [ ] Noch offen\n- [x] Bereits erfolgreich\n"
        editable = _render_test_documentation_markers(source, True)
        readonly = _render_test_documentation_markers(source, False)

        self.assertIn('data-checklist-line="1"', editable)
        self.assertIn('data-checklist-occurrence="1"', editable)
        self.assertIn(" checked>", editable)
        self.assertNotIn(" disabled", editable)
        self.assertIn(" disabled>", readonly)
