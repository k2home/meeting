from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class OrganizationBrandColorPreviewTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username="brand-preview-admin", email="brand-preview@example.test",
            password="strong-test-password",
        )

    def test_organization_settings_show_live_contrast_preview(self):
        self.client.force_login(self.admin)

        response = self.client.get(reverse("management_settings"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="brand-color-preview-mode"')
        self.assertContains(response, 'data-color-preview="primary"')
        self.assertContains(response, 'data-color-preview="secondary"')
        self.assertContains(response, 'data-color-preview="tertiary"')
        self.assertContains(response, "WCAG AA erfüllt")
        self.assertContains(response, "Kontrast");
        self.assertContains(response, '"#FFFFFF", "#243247", "#000000"')
        self.assertContains(response, "ratio >= 4.5")
