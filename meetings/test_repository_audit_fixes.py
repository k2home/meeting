from datetime import date, timedelta
import tempfile
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.db import IntegrityError, transaction
from django.test import TestCase, SimpleTestCase
from django.urls import reverse
from django.utils import timezone

from .forms import AttachmentForm, SeriesForm
from .models import AgendaItem, ArchivedMeetingAccess, AuditEvent, Meeting, MeetingSeries, SeriesAccess, Topic, TopicAttachment
from .services import ensure_agenda

User = get_user_model()


class ProtocolAndAgendaIntegrityTests(TestCase):
    def setUp(self):
        self.moderator = User.objects.create_user(username="audit-moderator", password="strong-test-password")
        self.member = User.objects.create_user(username="audit-member", password="strong-test-password")
        self.series = MeetingSeries.objects.create(name="Integritätsreihe")
        SeriesAccess.objects.create(user=self.moderator, series=self.series, role=SeriesAccess.ROLE_MODERATOR)
        SeriesAccess.objects.create(user=self.member, series=self.series, role=SeriesAccess.ROLE_PARTICIPANT)

    def test_moderator_without_staff_flag_sees_reopen_action(self):
        meeting = Meeting.objects.create(series=self.series, date=date(2026, 12, 1), finalized_at=timezone.now())
        self.assertFalse(self.moderator.is_staff)
        self.client.force_login(self.moderator)
        response = self.client.get(reverse("protocol", args=[meeting.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Besprechung wieder öffnen")
        self.assertContains(
            response,
            "data-confirm-message=\"Besprechung vom 01.12.2026 wieder öffnen?",
        )

    def test_finalized_meeting_does_not_receive_carried_agenda_items(self):
        previous = Meeting.objects.create(
            series=self.series, date=date(2026, 11, 1), finalized_at=timezone.now()
        )
        current = Meeting.objects.create(
            series=self.series, date=date(2026, 12, 1), finalized_at=timezone.now()
        )
        topic = Topic.objects.create(title="Nicht nachträglich übernehmen", series=self.series)
        AgendaItem.objects.create(meeting=previous, topic=topic, status="open")

        list(ensure_agenda(current))

        self.assertFalse(AgendaItem.objects.filter(meeting=current, topic=topic).exists())

    def test_reordering_agenda_is_audited(self):
        meeting = Meeting.objects.create(series=self.series, date=date(2026, 12, 2))
        first = Topic.objects.create(title="Alpha", series=self.series)
        second = Topic.objects.create(title="Beta", series=self.series)
        first_item = AgendaItem.objects.create(meeting=meeting, topic=first, position=0)
        second_item = AgendaItem.objects.create(meeting=meeting, topic=second, position=1)
        self.client.force_login(self.member)

        response = self.client.post(reverse("agenda_reorder", args=[meeting.pk]), {
            "item_ids": [str(second_item.pk), str(first_item.pk)]
        })

        self.assertEqual(response.status_code, 302)
        event = AuditEvent.objects.get(meeting=meeting, summary__contains="sortiert")
        self.assertEqual(event.changes["Reihenfolge"]["vorher"], ["Alpha", "Beta"])
        self.assertEqual(event.changes["Reihenfolge"]["nachher"], ["Beta", "Alpha"])


class MeetingSeriesValidationTests(TestCase):
    def test_series_form_rejects_end_date_before_start_date(self):
        today = timezone.localdate()
        form = SeriesForm(data={
            "name": "Ungültiger Zeitraum",
            "description": "",
            "recurrence": "weekly",
            "recurrence_interval": 1,
            "weekday": today.weekday(),
            "start_date": (today + timedelta(days=10)).isoformat(),
            "end_date": today.isoformat(),
        })
        self.assertFalse(form.is_valid())
        self.assertIn("end_date", form.errors)

    def test_database_rejects_invalid_date_range(self):
        today = timezone.localdate()
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                MeetingSeries.objects.create(
                    name="DB ungültiger Zeitraum",
                    start_date=today + timedelta(days=10),
                    end_date=today,
                )

    def test_series_model_and_database_enforce_interval_range(self):
        invalid = MeetingSeries(name="Intervall zu groß", recurrence_interval=53)
        with self.assertRaises(ValidationError):
            invalid.full_clean()
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                MeetingSeries.objects.create(name="DB Intervall zu groß", recurrence_interval=53)


class TopicArchiveWorkflowTests(TestCase):
    def setUp(self):
        self.moderator = User.objects.create_user(username="archive-moderator", password="strong-test-password")
        self.series = MeetingSeries.objects.create(name="Archiv-Reihe")
        SeriesAccess.objects.create(user=self.moderator, series=self.series, role=SeriesAccess.ROLE_MODERATOR)
        self.topic = Topic.objects.create(title="Archivthema", series=self.series)
        self.client.force_login(self.moderator)

    def test_topic_with_future_agenda_item_cannot_be_archived(self):
        meeting = Meeting.objects.create(
            series=self.series,
            date=timezone.localdate() + timedelta(days=7),
        )
        AgendaItem.objects.create(meeting=meeting, topic=self.topic)
        self.topic.status = "done"
        self.topic.completed_at = timezone.localdate() - timedelta(days=190)
        self.topic.save(update_fields=["status", "completed_at"])
        response = self.client.post(reverse("topic_archive_toggle", args=[self.topic.pk]))
        self.assertEqual(response.status_code, 302)
        self.topic.refresh_from_db()
        self.assertEqual(self.topic.status, "open")
        self.assertFalse(AuditEvent.objects.filter(topic=self.topic, action="archived").exists())

    def test_setting_topic_status_to_done_records_completion_date(self):
        response = self.client.post(reverse("topic_edit", args=[self.topic.pk]), {
            "save_topic_details": "1", "title": self.topic.title,
            "assigned_to": "", "status": "done",
        })
        self.assertEqual(response.status_code, 302)
        self.topic.refresh_from_db()
        self.assertEqual(self.topic.status, "done")
        self.assertEqual(self.topic.completed_at, timezone.localdate())

    def test_topic_must_be_done_before_archive(self):
        page = self.client.get(reverse("topic_edit", args=[self.topic.pk]))
        self.assertContains(page, "Das Thema kann erst archiviert werden")
        response = self.client.post(reverse("topic_archive_toggle", args=[self.topic.pk]))
        self.assertEqual(response.status_code, 302)
        self.topic.refresh_from_db()
        self.assertEqual(self.topic.status, "open")
        self.assertFalse(AuditEvent.objects.filter(topic=self.topic, action="archived").exists())

    def test_topic_cannot_be_archived_before_six_calendar_months(self):
        self.topic.status = "done"
        self.topic.completed_at = timezone.localdate() - timedelta(days=30)
        self.topic.save(update_fields=["status", "completed_at"])
        response = self.client.post(reverse("topic_archive_toggle", args=[self.topic.pk]))
        self.assertEqual(response.status_code, 302)
        self.topic.refresh_from_db()
        self.assertEqual(self.topic.status, "done")
        self.assertFalse(AuditEvent.objects.filter(topic=self.topic, action="archived").exists())

    @patch("meetings.agenda_topic_views._topic_testing_mode_enabled", return_value=True)
    def test_testing_mode_allows_immediate_archive_of_done_topic(self, _testing_mode):
        self.topic.status = "done"
        self.topic.completed_at = timezone.localdate()
        self.topic.save(update_fields=["status", "completed_at"])
        response = self.client.post(reverse("topic_archive_toggle", args=[self.topic.pk]))
        self.assertEqual(response.status_code, 302)
        self.topic.refresh_from_db()
        self.assertEqual(self.topic.status, "archived")

    def test_archiving_deletes_attachment_records_and_uploaded_files(self):
        with tempfile.TemporaryDirectory() as media_root:
            with override_settings(MEDIA_ROOT=media_root):
                attachment = TopicAttachment.objects.create(
                    topic=self.topic, label="Zu löschen",
                    uploaded_file=SimpleUploadedFile("anlage.txt", b"Dateiinhalt"),
                )
                stored_name = attachment.uploaded_file.name
                storage = attachment.uploaded_file.storage
                self.topic.status = "done"
                self.topic.completed_at = timezone.localdate() - timedelta(days=190)
                self.topic.save(update_fields=["status", "completed_at"])
                with self.captureOnCommitCallbacks(execute=True):
                    response = self.client.post(reverse("topic_archive_toggle", args=[self.topic.pk]))
                self.assertEqual(response.status_code, 302)
                self.assertFalse(TopicAttachment.objects.filter(pk=attachment.pk).exists())
                self.assertFalse(storage.exists(stored_name))
                archive_event = AuditEvent.objects.get(topic=self.topic, action="archived")
                self.assertEqual(archive_event.changes["Gelöschte Anlagen"][0]["filename"], "anlage.txt")
                archive_page = self.client.get(reverse("topic_edit", args=[self.topic.pk]))
                self.assertContains(archive_page, "anlage.txt")

    def test_archive_and_reopen_restores_previous_topic_status(self):
        self.topic.status = "done"
        self.topic.completed_at = timezone.localdate() - timedelta(days=190)
        self.topic.save(update_fields=["status", "completed_at"])

        archived = self.client.post(reverse("topic_archive_toggle", args=[self.topic.pk]))
        self.assertEqual(archived.status_code, 302)
        self.topic.refresh_from_db()
        self.assertEqual(self.topic.status, "archived")
        self.assertEqual(self.topic.archive_previous_status, "done")
        self.assertTrue(AuditEvent.objects.filter(topic=self.topic, action="archived").exists())

        archive_page = self.client.get(reverse("archive"))
        self.assertContains(archive_page, "Archivthema")

        reopened = self.client.post(reverse("topic_archive_toggle", args=[self.topic.pk]))
        self.assertEqual(reopened.status_code, 302)
        self.topic.refresh_from_db()
        self.assertEqual(self.topic.status, "done")
        self.assertEqual(self.topic.archive_previous_status, "")
        self.assertTrue(AuditEvent.objects.filter(topic=self.topic, action="reopened").exists())


class DeletedSeriesReadAccessTests(TestCase):
    def test_former_series_members_keep_read_access_to_retained_protocols_and_topics(self):
        moderator = User.objects.create_user(username="former-moderator", password="strong-test-password")
        member = User.objects.create_user(username="former-member", password="strong-test-password")
        series = MeetingSeries.objects.create(name="Zu löschende Reihe")
        SeriesAccess.objects.create(user=moderator, series=series, role=SeriesAccess.ROLE_MODERATOR)
        SeriesAccess.objects.create(user=member, series=series, role=SeriesAccess.ROLE_PARTICIPANT)
        meeting = Meeting.objects.create(series=series, date=date(2026, 11, 10))
        topic = Topic.objects.create(title="Historisches Thema", series=series)
        AgendaItem.objects.create(meeting=meeting, topic=topic, working_text="Gesicherter Inhalt")
        self.client.force_login(moderator)

        response = self.client.post(reverse("series_delete", args=[series.pk]), {"confirm": "yes"})

        self.assertEqual(response.status_code, 302)
        self.assertFalse(MeetingSeries.objects.filter(pk=series.pk).exists())
        self.assertEqual(ArchivedMeetingAccess.objects.filter(meeting=meeting).count(), 2)
        self.client.force_login(member)
        self.assertEqual(self.client.get(reverse("protocol", args=[meeting.pk])).status_code, 200)
        self.assertEqual(self.client.get(reverse("meeting", args=[meeting.pk])).status_code, 200)
        meeting.refresh_from_db()
        self.assertFalse(meeting.participants_initialized)
        self.assertEqual(self.client.get(reverse("topic_edit", args=[topic.pk])).status_code, 200)
        denied_topic_edit = self.client.post(reverse("topic_edit", args=[topic.pk]), {"title": "Manipuliert"})
        self.assertEqual(denied_topic_edit.status_code, 403)
        denied_meeting_edit = self.client.post(reverse("meeting", args=[meeting.pk]), {"save_participants": "1"})
        self.assertEqual(denied_meeting_edit.status_code, 403)


class AttachmentAndShiftSafetyTests(TestCase):
    def test_attachment_requires_file_or_network_reference(self):
        empty = AttachmentForm(data={"label": "Leere Anlage"})
        self.assertFalse(empty.is_valid())
        self.assertIn("__all__", empty.errors)

        link = AttachmentForm(data={"label": "Link", "network_path": "https://example.org/document"})
        self.assertTrue(link.is_valid())

        upload = SimpleUploadedFile("notiz.txt", b"Dateiinhalt", content_type="text/plain")
        file_form = AttachmentForm(data={"label": "Datei", "network_path": ""}, files={"uploaded_file": upload})
        self.assertTrue(file_form.is_valid())

    def test_failed_shift_rolls_back_working_text_change(self):
        member = User.objects.create_user(username="shift-member", password="strong-test-password")
        source = MeetingSeries.objects.create(name="Quellreihe")
        target = MeetingSeries.objects.create(name="Zielreihe")
        SeriesAccess.objects.create(user=member, series=source, role=SeriesAccess.ROLE_PARTICIPANT)
        SeriesAccess.objects.create(user=member, series=target, role=SeriesAccess.ROLE_PARTICIPANT)
        meeting = Meeting.objects.create(series=source, date=date(2026, 12, 1))
        target_meeting = Meeting.objects.create(series=target, date=date(2026, 12, 8))
        topic = Topic.objects.create(title="Verschiebung", series=source)
        item = AgendaItem.objects.create(meeting=meeting, topic=topic, working_text="Alter Text")
        self.client.force_login(member)

        with patch("meetings.views._move_future_agenda_items", side_effect=ValueError("Kollision")):
            response = self.client.post(reverse("meeting", args=[meeting.pk]), {
                "shift_item": str(item.pk),
                "target_series": str(target.pk),
                "target_meeting": str(target_meeting.pk),
                "working_text": "Neuer Text",
            })

        self.assertEqual(response.status_code, 302)
        item.refresh_from_db()
        self.assertEqual(item.working_text, "Alter Text")
        self.assertEqual(item.meeting, meeting)


class AuditTransactionAndTransferTests(TestCase):
    def setUp(self):
        self.moderator = User.objects.create_user(username="audit-tx-moderator", password="strong-test-password")
        self.series = MeetingSeries.objects.create(name="Audit Transaktion")
        SeriesAccess.objects.create(user=self.moderator, series=self.series, role=SeriesAccess.ROLE_MODERATOR)

    def test_topic_edit_rolls_back_when_audit_write_fails(self):
        topic = Topic.objects.create(title="Ursprünglicher Titel", series=self.series)
        self.client.force_login(self.moderator)
        with patch("meetings.agenda_topic_views.record_event", side_effect=RuntimeError("Audit ausgefallen")):
            with self.assertRaises(RuntimeError):
                self.client.post(reverse("topic_edit", args=[topic.pk]), {"title": "Neuer Titel"})
        topic.refresh_from_db()
        self.assertEqual(topic.title, "Ursprünglicher Titel")

    def test_topic_transfer_is_visible_in_source_and_destination_audit_histories(self):
        member = User.objects.create_user(username="transfer-member", password="strong-test-password")
        source = MeetingSeries.objects.create(name="Transfer Quelle")
        target = MeetingSeries.objects.create(name="Transfer Ziel")
        SeriesAccess.objects.create(user=member, series=source, role=SeriesAccess.ROLE_PARTICIPANT)
        SeriesAccess.objects.create(user=member, series=target, role=SeriesAccess.ROLE_PARTICIPANT)
        topic = Topic.objects.create(title="Zu übertragen", series=source)
        self.client.force_login(member)

        response = self.client.post(reverse("topic_transfer", args=[topic.pk]), {"series": target.pk})

        self.assertEqual(response.status_code, 302)
        event_series = set(AuditEvent.objects.filter(topic=topic, action="transferred").values_list("series_id", flat=True))
        self.assertEqual(event_series, {source.pk, target.pk})


class HstsConfigurationTests(SimpleTestCase):
    def test_preload_requires_subdomains_and_one_year(self):
        from config.settings import validate_hsts_configuration

        with self.assertRaises(ImproperlyConfigured):
            validate_hsts_configuration(31536000, False, True, True)
        with self.assertRaises(ImproperlyConfigured):
            validate_hsts_configuration(86400, True, True, True)
        with self.assertRaises(ImproperlyConfigured):
            validate_hsts_configuration(31536000, True, True, False)
        validate_hsts_configuration(31536000, True, True, True)
        validate_hsts_configuration(31536000, False, False, False)
