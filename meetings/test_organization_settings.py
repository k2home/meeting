from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from datetime import date
from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from .models import AuditEvent, OrganizationSettings, Topic


class OrganizationSettingsTests(TestCase):
    def test_organization_settings_page_keeps_all_controls_in_compact_card_layout(self):
        admin_user = get_user_model().objects.create_user(
            username="settings-layout-admin", password="strong-test-password"
        )
        admin_group, _ = Group.objects.get_or_create(name="Admin")
        admin_user.groups.add(admin_group)
        self.client.force_login(admin_user)

        response = self.client.get(reverse("management_settings"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'class="organization-settings-form"')
        self.assertContains(response, 'class="settings-card settings-card-wide"')
        self.assertContains(response, "grid-template-columns:repeat(2,minmax(0,1fr))")
        self.assertContains(response, "settings-logo-card")
        self.assertContains(response, 'class="organization-settings-layout"')
        self.assertContains(response, ".organization-settings-layout{display:grid;grid-template-columns:repeat(2,minmax(0,1fr))")
        self.assertContains(response, ".organization-settings-form{display:contents}")
        self.assertContains(response, ".organization-settings-form>section.settings-card:first-of-type{grid-column:1;grid-row:1}")
        self.assertContains(response, ".settings-logo-card{display:grid;grid-column:2;grid-row:1")
        self.assertContains(response, "@media(max-width:700px){.organization-settings-layout{grid-template-columns:minmax(0,1fr)}")
        self.assertContains(response, ".settings-logo-card{width:100%")
        self.assertContains(response, "Logo zurücksetzen")
        self.assertContains(response, 'value="reset_logo"')
        self.assertContains(response, "Neues Logo auswählen")
        self.assertContains(response, "grid-template-columns:minmax(0,1fr)")
        self.assertContains(response, "settings-logo-actions")
        self.assertContains(response, ".settings-logo-content{display:grid;grid-template-columns:repeat(2,minmax(0,1fr))")
        self.assertContains(response, ".settings-logo-preview img{display:block;width:100%;max-width:100%;max-height:140px")
        self.assertContains(response, '.settings-logo-form input[type="file"]{display:block;width:100%;max-width:100%;min-width:0')
        self.assertContains(response, "Noch kein Logo hinterlegt.")
        self.assertNotContains(response, 'type="checkbox"')
        self.assertNotContains(response, "Optionales Organisationslogo für die Seitenleiste")
        self.assertRegex(response.content.decode(), r'<input[^>]*type="number"[^>]*name="retention_years"|<input[^>]*name="retention_years"[^>]*type="number"')
        self.assertContains(response, 'min="1"')
        for field_name in (
            "logo",
            "name",
            "short_name",
            "timezone",
            "start_password",
            "attachment_max_size_mb",
            "retention_years",
            "primary_color",
            "primary_color_light",
            "primary_color_dark",
            "secondary_color",
            "secondary_color_light",
            "secondary_color_dark",
            "tertiary_color",
            "tertiary_color_light",
            "tertiary_color_dark",
        ):
            self.assertContains(response, f'name="{field_name}"')
        self.assertContains(response, 'value="save_logo"')
        self.assertContains(response, "Einstellungen speichern")
        self.assertContains(response, "timezone-live-preview")


    def test_admin_can_reset_organization_logo_with_dedicated_button(self):
        setting = OrganizationSettings.objects.create(
            name="Fachbereich Logo",
            logo=SimpleUploadedFile("organization-logo.png", b"logo-bytes", content_type="image/png"),
            logo_png=SimpleUploadedFile("organization-logo-converted.png", b"png-bytes", content_type="image/png"),
        )
        logo_name = setting.logo.name
        logo_png_name = setting.logo_png.name
        admin_user = get_user_model().objects.create_user(
            username="settings-logo-reset-admin", password="strong-test-password"
        )
        admin_group, _ = Group.objects.get_or_create(name="Admin")
        admin_user.groups.add(admin_group)
        self.client.force_login(admin_user)

        response = self.client.post(reverse("management_settings"), {"action": "reset_logo"})

        self.assertRedirects(response, reverse("management_settings"))
        setting.refresh_from_db()
        self.assertFalse(setting.logo)
        self.assertFalse(setting.logo_png)
        self.assertFalse(setting.logo.storage.exists(logo_name))
        self.assertFalse(setting.logo_png.storage.exists(logo_png_name))
        event = AuditEvent.objects.filter(summary="Organisationslogo zurückgesetzt").latest("pk")
        self.assertEqual(event.actor, admin_user)
        self.assertEqual(event.changes["Organisationslogo"]["nachher"], "Kein Logo")

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
        self.assertContains(response, 'type="text"')
        self.assertContains(response, 'value="AltesStartpasswort"')

        response = self.client.post(reverse("management_settings"), {
            "name": setting.name,
            "short_name": setting.short_name,
            "timezone": setting.timezone,
            "start_password": "einfach",
            "retention_years": setting.retention_years,
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

    def test_retention_setting_asks_before_changing_existing_archived_topics(self):
        setting = OrganizationSettings.objects.create(
            name="Fachbereich 10", retention_years=10
        )
        topic = Topic.objects.create(
            title="Bereits archiviert", status="archived",
            archived_at=date(2026, 8, 23),
        )
        admin_user = get_user_model().objects.create_user(
            username="retention-admin", password="strong-test-password"
        )
        admin_group, _ = Group.objects.get_or_create(name="Admin")
        admin_user.groups.add(admin_group)
        self.client.force_login(admin_user)
        payload = {
            "name": setting.name,
            "short_name": setting.short_name,
            "timezone": setting.timezone,
            "start_password": setting.start_password,
            "retention_years": "5",
            "attachment_max_size_mb": str(setting.attachment_max_size_mb),
            "primary_color": setting.primary_color,
            "primary_color_light": setting.primary_color_light,
            "primary_color_dark": setting.primary_color_dark,
            "secondary_color": setting.secondary_color,
            "secondary_color_light": setting.secondary_color_light,
            "secondary_color_dark": setting.secondary_color_dark,
            "tertiary_color": setting.tertiary_color,
            "tertiary_color_light": setting.tertiary_color_light,
            "tertiary_color_dark": setting.tertiary_color_dark,
        }

        response = self.client.post(reverse("management_settings"), payload)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["show_retention_confirmation"])
        setting.refresh_from_db()
        topic.refresh_from_db()
        self.assertEqual(setting.retention_years, 10)
        self.assertIsNone(topic.retention_years)

        response = self.client.post(
            reverse("management_settings"),
            {**payload, "retention_change_decision": "keep"},
        )

        self.assertRedirects(response, reverse("management_settings"))
        setting.refresh_from_db()
        topic.refresh_from_db()
        self.assertEqual(setting.retention_years, 5)
        self.assertEqual(topic.retention_years, 10)

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

        overview = self.client.get(reverse("auditor_overview"))
        self.assertEqual(overview.status_code, 200)
        self.assertNotContains(overview, "streng-geheim")
        self.assertIn("start_password", overview.context["organization_settings"].get_deferred_fields())

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

    def test_uploaded_svg_logo_is_served_with_a_restrictive_csp(self):
        from tempfile import TemporaryDirectory
        from django.core.files.uploadedfile import SimpleUploadedFile
        from django.test import override_settings

        with TemporaryDirectory() as media_root, override_settings(MEDIA_ROOT=media_root):
            setting = OrganizationSettings.objects.create(
                logo=SimpleUploadedFile(
                    "organization-logo.svg",
                    b'<svg xmlns="http://www.w3.org/2000/svg"><script>alert(1)</script><rect width="10" height="10"/></svg>',
                    content_type="image/svg+xml",
                )
            )
            user = get_user_model().objects.create_user(
                username="svg-logo-viewer", password="strong-test-password"
            )
            self.client.force_login(user)

            response = self.client.get(reverse("organization_logo"))

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response["Content-Type"], "image/svg+xml")
            self.assertIn("sandbox", response["Content-Security-Policy"])
            self.assertIn("default-src 'none'", response["Content-Security-Policy"])
            setting.refresh_from_db()
            self.assertTrue(setting.logo.name.endswith(".svg"))

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

    def test_timezone_and_branding_share_one_organization_settings_query(self):
        from django.test import RequestFactory
        from meetings.access import organization_branding
        from meetings.middleware import OrganizationTimezoneMiddleware

        OrganizationSettings.objects.create(
            name="Fachbereich 20",
            short_name="FB20",
            timezone="Europe/Paris",
            primary_color="#123456",
        )
        middleware = OrganizationTimezoneMiddleware(organization_branding)

        with self.assertNumQueries(1):
            branding = middleware(RequestFactory().get("/"))

        self.assertEqual(branding["organization_unit_name"], "Fachbereich 20")
        self.assertEqual(branding["organization_unit_short_name"], "FB20")
        self.assertEqual(branding["primary_color"], "#123456")
        self.assertEqual(branding["primary_color_light"], "#123456")

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
