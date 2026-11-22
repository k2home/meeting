from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import (
    AgendaItem, AuditEvent, Meeting, MeetingSeries, OrganizationSettings,
    SeriesAccess, Topic, TopicSnapshot, TopicAttachment,
)

User = get_user_model()


class FollowupDeletionIntegrityTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="chain-moderator", password="test-password")
        self.series = MeetingSeries.objects.create(name="Wiedervorlage-Kette")
        SeriesAccess.objects.create(user=self.user, series=self.series, role=SeriesAccess.ROLE_MODERATOR)
        self.client.force_login(self.user)
        today = timezone.localdate()
        self.meetings = [
            Meeting.objects.create(series=self.series, date=today + timedelta(days=offset))
            for offset in (1, 8, 15, 22)
        ]

    def test_deleting_middle_agenda_item_reconnects_predecessor_and_successor(self):
        predecessor_topic = Topic.objects.create(title="Vorheriger Punkt", series=self.series)
        deleted_topic = Topic.objects.create(title="Zu entfernender Punkt", series=self.series)
        successor_topic = Topic.objects.create(title="Späterer Punkt", series=self.series)
        predecessor = AgendaItem.objects.create(meeting=self.meetings[0], topic=predecessor_topic)
        deleted = AgendaItem.objects.create(
            meeting=self.meetings[1], topic=deleted_topic, followup_of=predecessor,
        )
        successor = AgendaItem.objects.create(
            meeting=self.meetings[2], topic=successor_topic, followup_of=deleted,
        )

        response = self.client.post(reverse("agenda_item_delete", args=[self.meetings[1].pk, deleted.pk]))

        self.assertEqual(response.status_code, 302)
        successor.refresh_from_db()
        self.assertEqual(successor.followup_of_id, predecessor.pk)
        self.assertFalse(AgendaItem.objects.filter(pk=deleted.pk).exists())

    def test_deleting_middle_item_without_predecessor_clears_successor_link(self):
        deleted_topic = Topic.objects.create(title="Punkt ohne Vorgänger", series=self.series)
        successor_topic = Topic.objects.create(title="Nachfolger ohne Vorgänger", series=self.series)
        deleted = AgendaItem.objects.create(meeting=self.meetings[1], topic=deleted_topic)
        successor = AgendaItem.objects.create(
            meeting=self.meetings[2], topic=successor_topic, followup_of=deleted,
        )

        self.client.post(reverse("agenda_item_delete", args=[self.meetings[1].pk, deleted.pk]))

        successor.refresh_from_db()
        self.assertIsNone(successor.followup_of_id)

    def test_meeting_delete_aborts_duplicate_merge_with_different_predecessors(self):
        topic = Topic.objects.create(title="Doppelter Punkt", series=self.series)
        first_parent = AgendaItem.objects.create(
            meeting=self.meetings[0],
            topic=Topic.objects.create(title="Vorgänger A", series=self.series),
        )
        second_parent = AgendaItem.objects.create(
            meeting=self.meetings[3],
            topic=Topic.objects.create(title="Vorgänger B", series=self.series),
        )
        source = AgendaItem.objects.create(
            meeting=self.meetings[1], topic=topic, followup_of=first_parent,
        )
        target = AgendaItem.objects.create(
            meeting=self.meetings[2], topic=topic, followup_of=second_parent,
        )

        response = self.client.post(reverse("meeting_delete", args=[self.meetings[1].pk]))

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Meeting.objects.filter(pk=self.meetings[1].pk).exists())
        self.assertTrue(AgendaItem.objects.filter(pk=source.pk).exists())
        target.refresh_from_db()
        self.assertEqual(target.followup_of_id, second_parent.pk)


class AdminIntegrityTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username="integrity-admin", email="admin@example.test", password="test-password",
        )
        self.client.force_login(self.admin)
        self.series = MeetingSeries.objects.create(name="Admin-Schutz")
        OrganizationSettings.objects.create(attachment_max_size_mb=1)

    def test_finalized_meeting_is_read_only_in_admin(self):
        meeting = Meeting.objects.create(
            series=self.series, date=timezone.localdate(), finalized_at=timezone.now(),
        )
        url = reverse("admin:meetings_meeting_change", args=[meeting.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'class="readonly"')
        self.assertNotContains(response, '<input type="date" name="date"')

    def test_snapshot_correction_requires_reason_and_records_previous_values(self):
        meeting = Meeting.objects.create(
            series=self.series, date=timezone.localdate(), finalized_at=timezone.now(),
        )
        snapshot = TopicSnapshot.objects.create(
            meeting=meeting, topic_title="Alter Titel", text="Alter Text",
            status="open", topic_id=123, responsible_name="Alt",
        )
        response = self.client.post(
            reverse("admin:meetings_topicsnapshot_change", args=[snapshot.pk]),
            {
                "topic_title": "Korrigierter Titel",
                "text": "Korrigierter Text",
                "status": "done",
                "topic_id": "123",
                "responsible_name": "Neu",
                "correction_reason": "Tippfehler im gesicherten Protokoll berichtigt.",
                "_save": "Speichern",
            },
        )
        self.assertEqual(response.status_code, 302)
        snapshot.refresh_from_db()
        self.assertEqual(snapshot.text, "Korrigierter Text")
        event = AuditEvent.objects.get(meeting=meeting, summary__startswith="Protokollkorrektur")
        correction = event.changes["Protokollkorrektur"]
        self.assertEqual(correction["vorher"]["text"], "Alter Text")
        self.assertEqual(correction["nachher"]["text"], "Korrigierter Text")
        self.assertEqual(correction["Begründung"], "Tippfehler im gesicherten Protokoll berichtigt.")

    def test_admin_attachment_upload_obeys_configured_limit(self):
        topic = Topic.objects.create(title="Upload-Prüfung", series=self.series)
        upload = SimpleUploadedFile("oversized.bin", b"x" * (1024 * 1024 + 1))
        response = self.client.post(
            reverse("admin:meetings_topicattachment_add"),
            {"topic": str(topic.pk), "label": "Zu groß", "network_path": "", "uploaded_file": upload},
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(TopicAttachment.objects.filter(label="Zu groß").exists())
        self.assertContains(response, "höchstens 1 MB")


class CsvCaseInsensitivePreviewTests(TestCase):
    def test_csv_preview_finds_existing_topic_ignoring_case(self):
        admin_user = User.objects.create_superuser(
            username="csv-admin", email="csv@example.test", password="test-password",
        )
        series = MeetingSeries.objects.create(name="CSV-Reihe")
        Topic.objects.create(title="Digitalisierung", series=series)
        self.client.force_login(admin_user)
        csv_text = (
            "record_type;series;topic_series;meeting_date;meeting_title;topic_title;"
            "topic_status;archive_previous_status;agenda_status;responsible_username;"
            "responsible_kurzbezeichnung;agenda_responsible_username;"
            "agenda_responsible_kurzbezeichnung;agenda_text;followup_series;followup_meeting_date\n"
            f"agenda;{series.name};{series.name};2026-12-18;Sitzung;DIGITALISIERUNG;"
            "open;;open;;;;Sachstand;;\n"
        )
        upload = SimpleUploadedFile("topics.csv", csv_text.encode("utf-8"), content_type="text/csv")

        response = self.client.post(
            reverse("admin:meetings_topic_csv_import"), {"csv_file": upload},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["preview"]["existing_topics"], 1)
        self.assertEqual(response.context["preview"]["new_topics"], 0)


class PartialFollowupSaveTests(TestCase):
    def test_bulk_text_save_reports_when_followup_is_not_created(self):
        user = User.objects.create_user(username="partial-save", password="test-password")
        series = MeetingSeries.objects.create(name="Teilweise Speicherung")
        SeriesAccess.objects.create(user=user, series=series, role=SeriesAccess.ROLE_MODERATOR)
        today = timezone.localdate()
        meeting = Meeting.objects.create(series=series, date=today + timedelta(days=1))
        target = Meeting.objects.create(series=series, date=today + timedelta(days=8))
        topic = Topic.objects.create(title="Doppelter Tagesordnungspunkt", series=series)
        source_item = AgendaItem.objects.create(meeting=meeting, topic=topic, working_text="Alt")
        AgendaItem.objects.create(meeting=target, topic=topic, working_text="Schon vorhanden")
        self.client.force_login(user)

        response = self.client.post(
            reverse("meeting", args=[meeting.pk]),
            {
                "save_all_working_texts": "1",
                f"working_text_{source_item.pk}": "Neuer gespeicherter Text",
                "schedule_item": str(source_item.pk),
                "target_series": str(series.pk),
                "target_meeting": str(target.pk),
            },
            follow=True,
        )

        source_item.refresh_from_db()
        self.assertEqual(source_item.working_text, "Neuer gespeicherter Text")
        self.assertFalse(AgendaItem.objects.filter(followup_of=source_item).exists())
        messages = [str(message) for message in response.context["messages"]]
        self.assertTrue(any("Wiedervorlage blieb unverändert" in message for message in messages))
