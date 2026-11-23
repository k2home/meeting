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

    def test_administrator_can_select_organization_timezone(self):
        setting = OrganizationSettings.objects.create(name="Fachbereich 10")
        admin_user = get_user_model().objects.create_superuser(
            username="timezone-admin",
            password="strong-test-password",
            email="timezone-admin@example.com",
        )
        self.client.force_login(admin_user)

        response = self.client.get(
            reverse("admin:meetings_organizationsettings_change", args=[setting.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Zeitzone")
        self.assertContains(response, 'value="Europe/Berlin"')

    def test_commit_timestamp_uses_organization_timezone(self):
        from .views import _format_commit_timestamp

        OrganizationSettings.objects.create(timezone="Europe/Paris")

        self.assertEqual(
            _format_commit_timestamp("2026-11-23T12:12:00+00:00"),
            "23.11.2026, 13:12 Uhr",
        )

    def test_request_uses_the_organization_timezone_globally(self):
        from django.test import RequestFactory
        from django.utils import timezone
        from .middleware import OrganizationTimezoneMiddleware

        OrganizationSettings.objects.create(timezone="Europe/Paris")
        middleware = OrganizationTimezoneMiddleware(
            lambda request: timezone.get_current_timezone_name()
        )

        with timezone.override("UTC"):
            active_timezone = middleware(RequestFactory().get("/"))

        self.assertEqual(active_timezone, "Europe/Paris")
        self.assertEqual(timezone.get_current_timezone_name(), "UTC")

    def test_central_datetime_format_includes_german_hour_suffix(self):
        from django.utils import formats
        from django.utils import timezone
        from datetime import datetime
        from zoneinfo import ZoneInfo

        value = timezone.make_aware(
            datetime(2026, 11, 23, 12, 12), ZoneInfo("UTC")
        )
        with timezone.override("Europe/Paris"):
            rendered = formats.date_format(
                timezone.localtime(value), "DATETIME_FORMAT"
            )

        self.assertEqual(rendered, "23.11.2026, 13:12 Uhr")
