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
