from datetime import date

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from .models import (
    AgendaItem, AuditEvent, Meeting, MeetingSeries, OrganizationSettings,
    Topic, TopicSnapshot,
)
from .retention import retention_expiry_date



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
            title="Laufendes Thema", series=self.series, status="in_progress"
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

        call_command("purge_expired_data")

        item.refresh_from_db()
        correction.refresh_from_db()
        self.assertEqual(item.working_text, "Text bleibt im Thema")
        self.assertFalse(TopicSnapshot.objects.filter(pk=snapshot.pk).exists())
        self.assertEqual(
            correction.changes["Protokollkorrektur"],
            {"Begründung": "Test"},
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
