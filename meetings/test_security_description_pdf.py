from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


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
