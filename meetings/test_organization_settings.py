from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import OrganizationSettings


class OrganizationSettingsTests(TestCase):
    def test_settings_are_a_single_global_record(self):
        first = OrganizationSettings.objects.create(name="Fachbereich 20")
        second = OrganizationSettings(name="Fachbereich 30")
        second.save()

        self.assertEqual(first.pk, 1)
        self.assertEqual(second.pk, 1)
        self.assertEqual(OrganizationSettings.objects.count(), 1)
        self.assertEqual(OrganizationSettings.current_name(), "Fachbereich 30")
        self.assertEqual(OrganizationSettings.current_short_name(), "MM")

    def test_short_label_is_visible_in_collapsed_navigation(self):
        OrganizationSettings.objects.create(name="Fachbereich 20", short_name="FB20")
        user = get_user_model().objects.create_user(
            username="short-branding-user", password="strong-test-password"
        )
        self.client.force_login(user)

        response = self.client.get(reverse("dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'class="brand-short">FB20</span>')

    def test_organization_unit_is_visible_on_login_page(self):
        OrganizationSettings.objects.create(name="Fachbereich 20")

        response = self.client.get(reverse("login"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Fachbereich 20")
        self.assertContains(response, "Meeting Manager")

    def test_organization_unit_is_visible_in_application_navigation(self):
        OrganizationSettings.objects.create(name="Fachbereich 20")
        user = get_user_model().objects.create_user(
            username="branding-user", password="strong-test-password"
        )
        self.client.force_login(user)

        response = self.client.get(reverse("dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Fachbereich 20")

    def test_administrator_can_edit_organization_unit_in_admin(self):
        setting = OrganizationSettings.objects.create(name="Fachbereich 10")
        admin_user = get_user_model().objects.create_superuser(
            username="branding-admin",
            password="strong-test-password",
            email="branding-admin@example.com",
        )
        self.client.force_login(admin_user)

        response = self.client.get(
            reverse("admin:meetings_organizationsettings_change", args=[setting.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Organisationseinheit")
        self.assertContains(response, "Fachbereich 10")
