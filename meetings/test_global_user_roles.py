from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .access import accessible_meetings, accessible_series, accessible_topics, has_writable_series, is_admin, is_auditor, is_moderator, is_reader
from .models import AuditEvent, Meeting, MeetingSeries, OrganizationSettings, SeriesAccess, Topic
from .user_roles import get_user_role, sync_user_role

User = get_user_model()


class GlobalUserRoleTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username="global-admin", email="admin@example.com", password="test-password"
        )
        self.series = MeetingSeries.objects.create(name="Vorstand")
        self.other_series = MeetingSeries.objects.create(name="Arbeitskreis")
        self.meeting = Meeting.objects.create(series=self.series, date="2026-12-01")
        self.topic = Topic.objects.create(title="Prüfthema", series=self.series)

    def test_global_roles_are_mutually_exclusive_and_staff_is_admin_only(self):
        user = User.objects.create_user(username="member", password="test-password")

        sync_user_role(user, "admin")
        user.refresh_from_db()
        self.assertEqual(get_user_role(user), "admin")
        self.assertTrue(is_admin(user))
        self.assertTrue(user.is_staff)

        sync_user_role(user, "auditor")
        user.refresh_from_db()
        self.assertEqual(get_user_role(user), "auditor")
        self.assertFalse(is_admin(user))
        self.assertTrue(is_auditor(user))
        self.assertFalse(user.is_staff)

        sync_user_role(user, "user")
        user.refresh_from_db()
        self.assertEqual(get_user_role(user), "user")
        self.assertFalse(is_auditor(user))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.groups.filter(name__in=["Admin", "Auditor"]).exists())

    def test_admin_does_not_inherit_series_access_from_global_role(self):
        self.assertTrue(is_admin(self.admin))
        self.assertFalse(is_moderator(self.admin, self.series))
        self.assertFalse(is_reader(self.admin, self.series))
        self.assertFalse(accessible_series(self.admin).exists())
        self.assertFalse(accessible_meetings(self.admin).exists())
        self.assertFalse(accessible_topics(self.admin).exists())

        self.client.force_login(self.admin)
        meeting_page = self.client.get(reverse("meeting", args=[self.meeting.pk]))
        self.assertEqual(meeting_page.status_code, 404)
        django_series_admin = self.client.get(reverse("admin:meetings_meetingseries_changelist"))
        django_meeting_admin = self.client.get(reverse("admin:meetings_meeting_changelist"))
        django_topic_admin = self.client.get(reverse("admin:meetings_topic_changelist"))
        self.assertEqual(django_series_admin.status_code, 403)
        self.assertEqual(django_meeting_admin.status_code, 403)
        self.assertEqual(django_topic_admin.status_code, 403)
        topic_csv_export = self.client.get(reverse("management_topic_csv_export"))
        self.assertEqual(topic_csv_export.status_code, 403)
        series_edit = self.client.post(reverse("series_edit", args=[self.series.pk]), {
            "name": self.series.name, "description": "Keine Admin-Vererbung",
            "recurrence": "weekly", "recurrence_interval": 1, "weekday": 1,
            "start_date": "2026-12-01",
        })
        self.assertEqual(series_edit.status_code, 403)

    def test_admin_with_reader_assignment_remains_read_only(self):
        SeriesAccess.objects.create(
            user=self.admin, series=self.series, role=SeriesAccess.ROLE_READER
        )
        self.assertTrue(is_reader(self.admin, self.series))
        self.assertFalse(is_moderator(self.admin, self.series))
        self.assertTrue(accessible_meetings(self.admin).filter(pk=self.meeting.pk).exists())

        self.client.force_login(self.admin)
        page = self.client.get(reverse("meeting", args=[self.meeting.pk]))
        self.assertEqual(page.status_code, 200)
        self.assertNotContains(page, "Teilnehmer speichern")
        update = self.client.post(
            reverse("meeting", args=[self.meeting.pk]), {"save_participants": "1"}
        )
        self.assertEqual(update.status_code, 403)
        topic_csv_export = self.client.get(reverse("management_topic_csv_export"))
        self.assertEqual(topic_csv_export.status_code, 403)

    def test_auditor_cannot_read_series_content_even_with_series_assignment(self):
        auditor = User.objects.create_user(username="auditor", password="test-password")
        sync_user_role(auditor, "auditor")

        SeriesAccess.objects.create(user=auditor, series=self.series, role=SeriesAccess.ROLE_MODERATOR)
        self.assertFalse(is_reader(auditor, self.series))
        self.assertFalse(is_moderator(auditor, self.series))
        self.assertFalse(has_writable_series(auditor))
        self.assertQuerySetEqual(
            accessible_series(auditor).order_by("pk"),
            MeetingSeries.objects.none(),
            transform=lambda item: item,
        )
        self.assertQuerySetEqual(
            accessible_meetings(auditor).order_by("pk"),
            Meeting.objects.none(),
            transform=lambda item: item,
        )
        self.assertQuerySetEqual(
            accessible_topics(auditor).order_by("pk"),
            Topic.objects.none(),
            transform=lambda item: item,
        )

    def test_user_csv_role_update_does_not_replace_existing_series_permissions(self):
        user = User.objects.create_user(username="member", email="member@example.com", password="test-password")
        assignment = SeriesAccess.objects.create(
            user=user, series=self.series, role=SeriesAccess.ROLE_MODERATOR
        )
        self.client.force_login(self.admin)
        upload = SimpleUploadedFile(
            "users.csv",
            b"username;email;user_role\nmember;member@example.com;auditor\n",
            content_type="text/csv",
        )
        preview = self.client.post(reverse("management_user_csv_import"), {"csv_file": upload})
        self.assertEqual(preview.status_code, 200)
        self.assertFalse(preview.context["errors"])
        response = self.client.post(
            reverse("management_user_csv_import"),
            {"action": "confirm", "token": preview.context["preview"]["token"]},
        )
        self.assertEqual(response.status_code, 302)
        user.refresh_from_db()
        self.assertEqual(get_user_role(user), "auditor")
        assignment.refresh_from_db()
        self.assertEqual(assignment.role, SeriesAccess.ROLE_MODERATOR)

    def test_auditor_cannot_read_or_change_meetings_or_topics(self):
        auditor = User.objects.create_user(username="auditor", password="test-password")
        sync_user_role(auditor, "auditor")
        self.client.force_login(auditor)

        meeting_page = self.client.get(reverse("meeting", args=[self.meeting.pk]))
        self.meeting.refresh_from_db()
        self.assertEqual(meeting_page.status_code, 404)
        self.assertFalse(self.meeting.participants_initialized)
        meeting_update = self.client.post(
            reverse("meeting", args=[self.meeting.pk]), {"save_participants": "1"}
        )
        topic_update = self.client.post(
            reverse("topic_edit", args=[self.topic.pk]), {"title": "Verändert"}
        )

        self.assertEqual(meeting_update.status_code, 403)
        self.assertEqual(topic_update.status_code, 403)
        self.topic.refresh_from_db()
        self.assertEqual(self.topic.title, "Prüfthema")

    def test_auditor_can_read_and_export_the_full_audit_history(self):
        auditor = User.objects.create_user(username="auditor", password="test-password")
        sync_user_role(auditor, "auditor")
        AuditEvent.objects.create(
            actor=self.admin, scope=AuditEvent.SCOPE_SYSTEM, action="created", summary="System-Audit-Eintrag sichtbar"
        )
        self.client.force_login(auditor)

        page = self.client.get(reverse("audit_history"))
        export = self.client.get(reverse("audit_history_csv"))

        self.assertEqual(page.status_code, 200)
        self.assertContains(page, "System-Audit-Eintrag sichtbar")
        self.assertContains(page, "nav-history")
        self.assertEqual(export.status_code, 200)
        self.assertIn("System-Audit-Eintrag sichtbar", export.content.decode("utf-8-sig"))


    def test_auditor_can_read_users_roles_and_organization_settings_but_not_start_password(self):
        auditor = User.objects.create_user(username="auditor", password="test-password")
        sync_user_role(auditor, "auditor")
        OrganizationSettings.objects.create(
            pk=1, name="Prüforganisation", short_name="Prüfung",
            start_password="streng-geheim",
        )
        self.client.force_login(auditor)

        users = self.client.get(reverse("auditor_users"))
        groups = self.client.get(reverse("auditor_groups"))
        organization = self.client.get(reverse("auditor_organization_settings"))

        self.assertEqual(users.status_code, 200)
        self.assertContains(users, "auditor")
        self.assertEqual(groups.status_code, 200)
        self.assertEqual(organization.status_code, 200)
        self.assertContains(organization, "Prüforganisation")
        self.assertNotContains(organization, "streng-geheim")

    def test_user_csv_export_contains_global_role_and_series_role(self):
        user = User.objects.create_user(username="member", password="test-password")
        sync_user_role(user, "auditor")
        SeriesAccess.objects.create(user=user, series=self.series, role=SeriesAccess.ROLE_READER)
        self.client.force_login(self.admin)

        response = self.client.get(reverse("management_user_csv_export"))

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"user_role", response.content)
        self.assertIn(b"auditor", response.content)
        self.assertIn(b"reader", response.content)
