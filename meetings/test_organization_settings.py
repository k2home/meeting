from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
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

    def test_admin_can_change_start_password_without_auditing_the_value(self):
        from .models import AuditEvent

        setting = OrganizationSettings.objects.create(name="Fachbereich 10", start_password="AltesStartpasswort")
        admin_user = get_user_model().objects.create_user(
            username="start-password-admin", password="strong-test-password"
        )
        admin_group, _ = Group.objects.get_or_create(name="Admin")
        admin_user.groups.add(admin_group)
        self.client.force_login(admin_user)

        response = self.client.get(reverse("management_settings"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'type="password"')
        self.assertContains(response, 'value="AltesStartpasswort"')

        response = self.client.post(reverse("management_settings"), {
            "name": setting.name,
            "short_name": setting.short_name,
            "timezone": setting.timezone,
            "start_password": "einfach",
            "attachment_max_size_mb": setting.attachment_max_size_mb,
            "primary_color": setting.primary_color,
            "primary_color_light": setting.primary_color_light,
            "primary_color_dark": setting.primary_color_dark,
            "secondary_color": setting.secondary_color,
            "secondary_color_light": setting.secondary_color_light,
            "secondary_color_dark": setting.secondary_color_dark,
            "tertiary_color": setting.tertiary_color,
            "tertiary_color_light": setting.tertiary_color_light,
            "tertiary_color_dark": setting.tertiary_color_dark,
        })

        self.assertRedirects(response, reverse("management_settings"))
        setting.refresh_from_db()
        self.assertEqual(setting.start_password, "einfach")
        event = AuditEvent.objects.filter(summary="Organisationseinstellungen geändert").latest("pk")
        self.assertNotIn("einfach", str(event.changes))
        self.assertEqual(event.changes["Startpasswort"]["nachher"], "Geändert")

    def test_auditor_cannot_read_start_password(self):
        setting = OrganizationSettings.objects.create(name="Fachbereich 10", start_password="streng-geheim")
        auditor = get_user_model().objects.create_user(
            username="start-password-auditor", password="strong-test-password"
        )
        auditor_group, _ = Group.objects.get_or_create(name="Auditor")
        auditor.groups.add(auditor_group)
        self.client.force_login(auditor)

        response = self.client.get(reverse("auditor_organization_settings"))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "streng-geheim")
        self.assertIn("start_password", response.context["settings"].get_deferred_fields())
        setting.refresh_from_db()
        self.assertEqual(setting.start_password, "streng-geheim")

    def test_password_setup_uses_configured_organization_password(self):
        from .password_setup import start_password_setup

        OrganizationSettings.objects.create(start_password="beliebig")
        user = get_user_model().objects.create_user(
            username="configured-start-password", password="old-password"
        )

        profile = start_password_setup(user)

        user.refresh_from_db()
        self.assertTrue(user.check_password("beliebig"))
        self.assertTrue(profile.must_change_password)
        self.assertIsNotNone(profile.password_setup_expires_at)

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
        get_user_model().objects.create_user(username="login-branding-user", password="strong-test-password")
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
            restored_timezone = timezone.get_current_timezone_name()

        self.assertEqual(active_timezone, "Europe/Paris")
        self.assertEqual(restored_timezone, "UTC")

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
