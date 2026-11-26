from django.contrib.auth import get_user_model
from django.test import TestCase
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
    def test_test_documentation_requires_authentication(self):
        response = self.client.get(reverse("test_documentation"))
        self.assertEqual(response.status_code, 302)

    def test_authenticated_user_can_open_interactive_test_checklist(self):
        user = get_user_model().objects.create_user(
            username="test-documentation-reader", password="Strong-test-password-123!"
        )
        self.client.force_login(user)

        response = self.client.get(reverse("test_documentation"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Prüfung des Verfahrens")
        self.assertContains(response, 'type="checkbox"')
        self.assertContains(response, "Test erfolgreich")
        self.assertContains(response, reverse("user_guide"))

    def test_user_guide_links_to_test_documentation(self):
        user = get_user_model().objects.create_user(
            username="test-documentation-guide-reader", password="Strong-test-password-123!"
        )
        self.client.force_login(user)

        response = self.client.get(reverse("user_guide"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse("test_documentation"))
        self.assertContains(response, "Prüfung des Verfahrens – Testcheckliste")



class GitBackedTestChecklistTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="git-checklist-reader", password="Strong-test-password-123!")
        self.client.force_login(self.user)

    def test_checkbox_marker_is_updated_in_markdown_source(self):
        from meetings.guide_views import _apply_test_documentation_checkbox
        source = "# Bereich\n- [ ] Erster Test\n- [x] Zweiter Test\n"
        updated = _apply_test_documentation_checkbox(source, "line-2-1", True)
        self.assertEqual(updated, "# Bereich\n- [x] Erster Test\n- [x] Zweiter Test\n")
        unchecked = _apply_test_documentation_checkbox(updated, "line-3-1", False)
        self.assertEqual(unchecked, "# Bereich\n- [x] Erster Test\n- [ ] Zweiter Test\n")

    @patch("meetings.guide_views._test_documentation_github_configured", return_value=True)
    @patch("meetings.guide_views._save_test_documentation_checkbox")
    def test_checkbox_click_is_committed_to_markdown_without_database_state(self, save_checkbox, _configured):
        response = self.client.post(reverse("test_documentation_toggle"), {"checkbox_id": "line-38-1", "checked": "true"})
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"success": True, "checked": True})
        save_checkbox.assert_called_once_with("line-38-1", True)

    @patch("meetings.guide_views._test_documentation_github_configured", return_value=False)
    def test_checkbox_save_is_rejected_if_github_is_not_configured(self, _configured):
        response = self.client.post(reverse("test_documentation_toggle"), {"checkbox_id": "line-38-1", "checked": "true"})
        self.assertEqual(response.status_code, 503)

    def test_checkbox_update_requires_authentication_and_post(self):
        self.client.logout()
        response = self.client.post(reverse("test_documentation_toggle"), {"checkbox_id": "line-38-1", "checked": "true"})
        self.assertEqual(response.status_code, 302)
        self.client.force_login(self.user)
        response = self.client.get(reverse("test_documentation_toggle"))
        self.assertEqual(response.status_code, 405)

    def test_checkbox_update_rejects_invalid_values(self):
        response = self.client.post(reverse("test_documentation_toggle"), {"checkbox_id": "../settings", "checked": "true"})
        self.assertEqual(response.status_code, 400)
        response = self.client.post(reverse("test_documentation_toggle"), {"checkbox_id": "line-38-1", "checked": "maybe"})
        self.assertEqual(response.status_code, 400)
