from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .access import accessible_meetings, accessible_series, accessible_topics, has_writable_series, is_admin, is_auditor, is_moderator, is_reader
from .models import AuditEvent, Meeting, MeetingSeries, SeriesAccess, Topic
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

    def test_admin_cannot_demote_own_global_role(self):
        admin = User.objects.create_user(username="self-demoting-admin", password="test-password")
        sync_user_role(admin, "admin")
        self.client.force_login(admin)

        response = self.client.post(reverse("management_user_edit", args=[admin.pk]), {
            "username": admin.username,
            "first_name": "",
            "last_name": "",
            "email": "",
            "is_active": "true",
            "role": "user",
            "short_description": "",
        })

        self.assertEqual(response.status_code, 200)
        self.assertIn("role", response.context["form"].errors)
        admin.refresh_from_db()
        self.assertEqual(get_user_role(admin), "admin")
        self.assertTrue(admin.is_staff)

    def test_django_admin_disables_global_role_when_editing_own_admin_account(self):
        admin = User.objects.create_user(username="admin-ui-self", password="test-password")
        sync_user_role(admin, "admin")
        self.client.force_login(admin)

        response = self.client.get(reverse("admin:auth_user_change", args=[admin.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["adminform"].form.fields["role"].disabled)
        self.assertTrue(response.context["adminform"].form.fields["is_active"].disabled)

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

    def test_auditor_can_read_all_series_but_has_no_write_access(self):
        auditor = User.objects.create_user(username="auditor", password="test-password")
        sync_user_role(auditor, "auditor")

        SeriesAccess.objects.create(user=auditor, series=self.series, role=SeriesAccess.ROLE_MODERATOR)
        self.assertTrue(is_reader(auditor, self.series))
        self.assertFalse(is_moderator(auditor, self.series))
        self.assertFalse(has_writable_series(auditor))
        self.assertQuerySetEqual(
            accessible_series(auditor).order_by("pk"),
            MeetingSeries.objects.order_by("pk"),
            transform=lambda item: item,
        )
        self.assertQuerySetEqual(
            accessible_meetings(auditor).order_by("pk"),
            Meeting.objects.order_by("pk"),
            transform=lambda item: item,
        )
        self.assertQuerySetEqual(
            accessible_topics(auditor).order_by("pk"),
            Topic.objects.order_by("pk"),
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

    def test_auditor_cannot_change_meetings_or_topics(self):
        auditor = User.objects.create_user(username="auditor", password="test-password")
        sync_user_role(auditor, "auditor")
        self.client.force_login(auditor)

        meeting_page = self.client.get(reverse("meeting", args=[self.meeting.pk]))
        self.meeting.refresh_from_db()
        self.assertEqual(meeting_page.status_code, 200)
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
            actor=self.admin, series=self.series, action="created", summary="Audit-Eintrag sichtbar"
        )
        self.client.force_login(auditor)

        page = self.client.get(reverse("audit_history"))
        export = self.client.get(reverse("audit_history_csv"))

        self.assertEqual(page.status_code, 200)
        self.assertContains(page, "Audit-Eintrag sichtbar")
        self.assertContains(page, "nav-history")
        self.assertEqual(export.status_code, 200)
        self.assertIn("Audit-Eintrag sichtbar", export.content.decode("utf-8-sig"))

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
