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


class SharedTestChecklistPersistenceTests(TestCase):
    def setUp(self):
        self.user_one = get_user_model().objects.create_user(
            username="checklist-user-one", password="Strong-test-password-123!"
        )
        self.user_two = get_user_model().objects.create_user(
            username="checklist-user-two", password="Strong-test-password-123!"
        )

    def test_checkbox_change_is_saved_and_shared_between_users(self):
        self.client.force_login(self.user_one)
        response = self.client.post(reverse("test_documentation_toggle"), {
            "checkbox_id": "line-38-1",
            "checked": "true",
        })
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"success": True, "checked": True})

        self.client.force_login(self.user_two)
        page = self.client.get(reverse("test_documentation"))
        self.assertEqual(page.status_code, 200)
        self.assertContains(page, 'data-checklist-id="line-38-1" checked')

    def test_checkbox_can_be_unchecked_again(self):
        from meetings.models import TestChecklistState

        TestChecklistState.objects.create(state={"line-38-1": True})
        self.client.force_login(self.user_one)
        response = self.client.post(reverse("test_documentation_toggle"), {
            "checkbox_id": "line-38-1",
            "checked": "false",
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(TestChecklistState.objects.get(pk=1).state["line-38-1"])

    def test_checkbox_update_requires_authentication_and_post(self):
        response = self.client.post(reverse("test_documentation_toggle"), {
            "checkbox_id": "line-38-1", "checked": "true",
        })
        self.assertEqual(response.status_code, 302)
        self.client.force_login(self.user_one)
        response = self.client.get(reverse("test_documentation_toggle"))
        self.assertEqual(response.status_code, 405)

    def test_checkbox_update_rejects_invalid_values(self):
        self.client.force_login(self.user_one)
        response = self.client.post(reverse("test_documentation_toggle"), {
            "checkbox_id": "../settings", "checked": "true",
        })
        self.assertEqual(response.status_code, 400)
        response = self.client.post(reverse("test_documentation_toggle"), {
            "checkbox_id": "line-38-1", "checked": "maybe",
        })
        self.assertEqual(response.status_code, 400)
