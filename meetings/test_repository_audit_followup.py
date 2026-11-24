from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase, SimpleTestCase
from django.urls import reverse
from django.utils import timezone

from .models import AgendaItem, AuditEvent, Meeting, MeetingSeries, SeriesAccess, Topic
from .topic_csv import _csv_value

User = get_user_model()


class CsvSafetyRegressionTests(SimpleTestCase):
    def test_topic_export_escapes_actual_control_characters_and_formula_prefixes(self):
        for value in ("\t=1+1", "\r=1+1", "=1+1", "+1+1", "-1+1", "@SUM(A1)"):
            with self.subTest(value=repr(value)):
                self.assertEqual(_csv_value(value), "'" + value)


class UserCsvAdministratorSyncTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username="csv-admin-sync", email="csv-admin-sync@example.com", password="test-password"
        )
        self.client.force_login(self.admin)

    def _import(self, username, email, administrator):
        from django.core.files.uploadedfile import SimpleUploadedFile

        csv_text = (
            "username;email;is_administrator\n"
            f"{username};{email};{'true' if administrator else 'false'}\n"
        )
        upload = SimpleUploadedFile("users.csv", csv_text.encode("utf-8"), content_type="text/csv")
        preview = self.client.post(reverse("admin:auth_user_csv_import"), {"csv_file": upload})
        self.assertEqual(preview.status_code, 200)
        self.assertIsNotNone(preview.context["preview"])
        return self.client.post(
            reverse("admin:auth_user_csv_import"),
            {"action": "confirm", "token": preview.context["preview"]["token"]},
        )

    def test_csv_admin_role_sets_and_clears_group_and_staff_flag(self):
        self._import("csv-admin-role", "csv-admin-role@example.com", True)
        user = User.objects.get(username="csv-admin-role")
        self.assertTrue(user.groups.filter(name="Admin").exists())
        self.assertTrue(user.is_staff)

        self._import("csv-admin-role", "csv-admin-role@example.com", False)
        user.refresh_from_db()
        self.assertFalse(user.groups.filter(name="Admin").exists())
        self.assertFalse(user.is_staff)

    def test_csv_removing_admin_group_does_not_remove_superuser_staff_access(self):
        self._import("csv-admin-super", "csv-admin-super@example.com", True)
        user = User.objects.get(username="csv-admin-super")
        user.is_superuser = True
        user.save(update_fields=["is_superuser"])

        self._import("csv-admin-super", "csv-admin-super@example.com", False)
        user.refresh_from_db()
        self.assertFalse(user.groups.filter(name="Admin").exists())
        self.assertTrue(user.is_staff)


class MeetingSeriesAuditAndValidationTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username="series-audit-admin", email="series-audit-admin@example.com", password="test-password"
        )
        self.client.force_login(self.admin)

    def test_series_creation_and_edit_are_audited(self):
        today = timezone.localdate()
        moderator = User.objects.create_user(
            username="initial-series-moderator", first_name="Ada", last_name="Lovelace",
            password="test-password",
        )
        response = self.client.post(reverse("series_admin"), {
            "initial_moderator": moderator.pk,
            "name": "Auditierte Reihe",
            "description": "Vorher",
            "recurrence": "weekly",
            "recurrence_interval": 1,
            "weekday": today.weekday(),
            "start_date": today.isoformat(),
            "end_date": (today + timedelta(days=60)).isoformat(),
        })
        self.assertEqual(response.status_code, 302)
        series = MeetingSeries.objects.get(name="Auditierte Reihe")
        created_event = AuditEvent.objects.get(series=series, action="created")
        self.assertEqual(created_event.actor, self.admin)
        self.assertTrue(SeriesAccess.objects.filter(
            series=series, user=moderator, role=SeriesAccess.ROLE_MODERATOR
        ).exists())
        self.assertFalse(SeriesAccess.objects.filter(series=series, user=self.admin).exists())
        self.assertEqual(created_event.changes["Erster Moderator"]["nachher"], "Ada Lovelace")

        response = self.client.post(reverse("series_edit", args=[series.pk]), {
            "name": "Auditierte Reihe",
            "description": "Nachher",
            "recurrence": "weekly",
            "recurrence_interval": 1,
            "weekday": today.weekday(),
            "start_date": today.isoformat(),
            "end_date": (today + timedelta(days=60)).isoformat(),
        })
        self.assertEqual(response.status_code, 302)
        updated_event = AuditEvent.objects.get(series=series, action="updated")
        self.assertEqual(updated_event.changes["Beschreibung"], {
            "vorher": "Vorher", "nachher": "Nachher",
        })

    def test_series_extension_rolls_back_when_audit_write_fails(self):
        today = timezone.localdate()
        previous_end = today + timedelta(days=5)
        series = MeetingSeries.objects.create(
            name="Rollback Verlängerung", recurrence="weekly", weekday=today.weekday(),
            start_date=today, end_date=previous_end,
        )
        with patch("meetings.views.record_event", side_effect=RuntimeError("Audit unavailable")):
            with self.assertRaises(RuntimeError):
                self.client.post(reverse("series_extend", args=[series.pk]))

        series.refresh_from_db()
        self.assertEqual(series.end_date, previous_end)
        self.assertFalse(AuditEvent.objects.filter(series=series, action="series_extended").exists())

    def test_series_reset_rolls_back_when_audit_write_fails(self):
        today = timezone.localdate()
        first_date = today
        series = MeetingSeries.objects.create(
            name="Rollback Reset", recurrence="weekly", weekday=first_date.weekday(),
            start_date=first_date, end_date=first_date + timedelta(days=28),
        )
        meeting = Meeting.objects.create(series=series, date=first_date)
        topic = Topic.objects.create(title="Reset Inhalt", series=series)
        AgendaItem.objects.create(meeting=meeting, topic=topic, working_text="Erhaltener Text")

        with patch("meetings.views.record_event", side_effect=RuntimeError("Audit unavailable")):
            with self.assertRaises(RuntimeError):
                self.client.post(reverse("series_reset_meetings", args=[series.pk]))

        self.assertTrue(Meeting.objects.filter(pk=meeting.pk).exists())
        self.assertTrue(AgendaItem.objects.filter(meeting=meeting, topic=topic).exists())
        self.assertFalse(AuditEvent.objects.filter(series=series, action="series_reset").exists())

    def test_weekday_validation_and_database_constraint(self):
        invalid = MeetingSeries(name="Ungültiger Wochentag", weekday=7)
        with self.assertRaises(ValidationError):
            invalid.full_clean()
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                MeetingSeries.objects.create(name="Ungültiger DB-Wochentag", weekday=7)
        self.assertEqual(invalid.weekday_label, "Ungültiger Wochentag")


class PermissionMatrixDocumentationTests(SimpleTestCase):
    def test_readme_describes_audit_history_as_moderator_and_admin_only(self):
        from pathlib import Path

        readme = Path(__file__).resolve().parents[1] / "README.md"
        content = readme.read_text(encoding="utf-8")
        self.assertIn("Änderungsverlauf ansehen | Nein | Nein | Ja, eigene moderierte Reihen | Alle Reihen", content)
        self.assertIn("Berechtigungsmatrix nach Funktionsbereichen", content)
