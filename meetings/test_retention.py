from datetime import date, timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from .access import accessible_retained_agenda_entries, accessible_topics
from .models import (
    AgendaItem, AuditEvent, Meeting, MeetingSeries, OrganizationSettings,
    RetainedAgendaEntry, SeriesAccess, Topic, TopicSnapshot,
)
from .retention import protocol_deletion_date, retention_expiry_date



class RetentionCleanupTests(TestCase):
    def test_retention_runs_from_first_january_after_reference_year(self):
        self.assertEqual(
            retention_expiry_date(date(2026, 8, 23), 5),
            date(2031, 12, 31),
        )

    def setUp(self):
        OrganizationSettings.objects.create(name="Test", retention_years=1)
        self.series = MeetingSeries.objects.create(
            name="Retention Test", start_date=date(2010, 1, 1)
        )
        self.user = get_user_model().objects.create_user(
            username="retention-test", password="test-password"
        )

    @patch("meetings.management.commands.purge_expired_data.timezone.localdate")
    def test_archived_topic_is_kept_on_expiry_date_and_deleted_the_next_day(self, localdate):
        expiry = date(2021, 12, 31)
        topic = Topic.objects.create(
            title="Grenzfall Aufbewahrung", series=self.series, status="archived",
            archived_at=date(2020, 8, 23), retention_years=1,
        )

        localdate.return_value = expiry
        call_command("purge_expired_data")
        self.assertTrue(Topic.objects.filter(pk=topic.pk).exists())

        localdate.return_value = expiry + timedelta(days=1)
        call_command("purge_expired_data")
        self.assertFalse(Topic.objects.filter(pk=topic.pk).exists())

    def test_protocol_deletion_date_uses_global_not_topic_retention(self):
        topic = Topic.objects.create(
            title="Individuelle Themenfrist", series=self.series,
            status="in_progress", retention_years=50,
        )
        meeting = Meeting.objects.create(
            series=self.series, date=date(2026, 8, 23), finalized_at=timezone.now()
        )

        self.assertEqual(
            protocol_deletion_date(meeting, topic),
            date(2027, 12, 31),
        )

    def test_archived_topic_and_all_its_content_are_deleted_after_expiry(self):
        topic = Topic.objects.create(
            title="Abgelaufenes Thema", series=self.series, status="archived",
            archived_at=date(2010, 8, 23), retention_years=1,
        )
        meeting = Meeting.objects.create(
            series=self.series, date=date(2010, 8, 23), finalized_at=timezone.now()
        )
        item = AgendaItem.objects.create(
            meeting=meeting, topic=topic, working_text="Protokolltext"
        )
        snapshot = TopicSnapshot.objects.create(
            meeting=meeting, topic_id=topic.pk, topic_title=topic.title,
            text="Gesicherter Protokolltext", status="done",
        )
        event = AuditEvent.objects.create(
            topic=topic, meeting=meeting, actor=self.user, action="archived",
            summary="Thema archiviert",
        )

        call_command("purge_expired_data")

        self.assertFalse(Topic.objects.filter(pk=topic.pk).exists())
        self.assertFalse(AgendaItem.objects.filter(pk=item.pk).exists())
        self.assertFalse(TopicSnapshot.objects.filter(pk=snapshot.pk).exists())
        self.assertFalse(AuditEvent.objects.filter(pk=event.pk).exists())

    def test_expired_snapshot_is_removed_but_active_topic_text_is_retained(self):
        topic = Topic.objects.create(
            title="Laufendes Thema", series=self.series, status="in_progress",
            retention_years=50,
        )
        meeting = Meeting.objects.create(
            series=self.series, date=date(2010, 8, 23), finalized_at=timezone.now()
        )
        item = AgendaItem.objects.create(
            meeting=meeting, topic=topic, working_text="Text bleibt im Thema"
        )
        snapshot = TopicSnapshot.objects.create(
            meeting=meeting, topic_id=topic.pk, topic_title=topic.title,
            text="Gesicherter Protokollstand", status="in_progress",
        )
        correction = AuditEvent.objects.create(
            meeting=meeting, actor=self.user, action="updated",
            summary="Protokollkorrektur",
            changes={"Protokollkorrektur": {
                "Begründung": "Test",
                "vorher": {"topic_id": topic.pk, "text": "Alter Snapshot"},
                "nachher": {"topic_id": topic.pk, "text": "Korrigierter Snapshot"},
            }},
        )
        agenda_edit = AuditEvent.objects.create(
            meeting=meeting, topic=topic, actor=self.user, action="agenda_edited",
            summary="Tagesordnungstext geändert",
            changes={"Text": {"vorher": "Alter Text", "nachher": "Neuer Text"}},
        )

        call_command("purge_expired_data")

        correction.refresh_from_db()
        agenda_edit.refresh_from_db()
        self.assertFalse(Meeting.objects.filter(pk=meeting.pk).exists())
        self.assertFalse(AgendaItem.objects.filter(pk=item.pk).exists())
        self.assertFalse(TopicSnapshot.objects.filter(pk=snapshot.pk).exists())
        retained = RetainedAgendaEntry.objects.get(topic=topic, original_meeting_id=meeting.pk)
        self.assertEqual(retained.working_text, "Text bleibt im Thema")
        self.assertEqual(retained.meeting_date, date(2010, 8, 23))
        self.assertEqual(topic.status, "in_progress")
        self.assertEqual(
            correction.changes["Protokollkorrektur"],
            {"Begründung": "Test"},
        )
        self.assertEqual(agenda_edit.changes, {})

    def test_meeting_retention_uses_global_period_not_topic_override(self):
        OrganizationSettings.objects.filter(pk=1).update(retention_years=10)
        topic = Topic.objects.create(
            title="Kurze Themenfrist", series=self.series, status="in_progress",
            retention_years=1,
        )
        meeting = Meeting.objects.create(
            series=self.series, date=date(2020, 8, 23), finalized_at=timezone.now()
        )
        item = AgendaItem.objects.create(
            meeting=meeting, topic=topic, working_text="Bleibt bis zur globalen Frist"
        )

        call_command("purge_expired_data")

        self.assertTrue(Meeting.objects.filter(pk=meeting.pk).exists())
        self.assertTrue(AgendaItem.objects.filter(pk=item.pk).exists())
        self.assertFalse(RetainedAgendaEntry.objects.filter(topic=topic).exists())

    def test_retained_agenda_keeps_original_series_access_after_series_deletion(self):
        topic = Topic.objects.create(
            title="Thema mit historischer Berechtigung", series=self.series,
            status="in_progress",
        )
        meeting = Meeting.objects.create(
            series=self.series, date=date(2010, 8, 23), finalized_at=timezone.now()
        )
        AgendaItem.objects.create(
            meeting=meeting, topic=topic, working_text="Nur für Serienmitglieder"
        )
        SeriesAccess.objects.create(
            user=self.user, series=self.series, role=SeriesAccess.ROLE_READER
        )

        call_command("purge_expired_data")

        entry = RetainedAgendaEntry.objects.get(topic=topic)
        self.assertTrue(entry.access_users.filter(pk=self.user.pk).exists())
        self.assertTrue(
            accessible_retained_agenda_entries(self.user).filter(pk=entry.pk).exists()
        )

        self.series.delete()

        self.assertTrue(accessible_topics(self.user).filter(pk=topic.pk).exists())
        outsider = get_user_model().objects.create_user(
            username="retention-outsider", password="test-password"
        )
        self.assertFalse(
            accessible_retained_agenda_entries(outsider).filter(pk=entry.pk).exists()
        )

    def test_reopened_protocol_copy_in_audit_history_also_expires(self):
        topic = Topic.objects.create(
            title="Laufendes Thema", series=self.series, status="in_progress"
        )
        meeting = Meeting.objects.create(
            series=self.series, date=date(2010, 8, 23), finalized_at=None
        )
        event = AuditEvent.objects.create(
            meeting=meeting, actor=self.user, action="reopened",
            summary="Besprechung wieder geöffnet",
            changes={"Gesicherter Protokollstand": [
                {"topic_id": topic.pk, "topic_title": topic.title, "text": "Alter Protokolltext"},
                {"topic_id": topic.pk + 999, "topic_title": "Anderes Thema", "text": "Bleibt"},
            ]},
        )

        call_command("purge_expired_data")

        event.refresh_from_db()
        self.assertEqual(
            event.changes["Gesicherter Protokollstand"],
            [{"topic_id": topic.pk + 999, "topic_title": "Anderes Thema", "text": "Bleibt"}],
        )
