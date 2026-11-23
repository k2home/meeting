from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import AgendaItem, Meeting, MeetingSeries, SeriesAccess, Topic
from .services import finalize_meeting


class ProtocolFollowupDateTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            username="protocol-followup-user",
            password="strong-test-password",
        )
        self.series = MeetingSeries.objects.create(name="Protokoll-Wiedervorlage")
        SeriesAccess.objects.create(
            user=self.user,
            series=self.series,
            role=SeriesAccess.ROLE_MODERATOR,
        )
        self.meeting = Meeting.objects.create(
            series=self.series,
            date=date(2026, 11, 2),
        )
        self.followup_meeting = Meeting.objects.create(
            series=self.series,
            date=date(2026, 12, 7),
        )
        self.topic = Topic.objects.create(
            title="Wiedervorlage im Protokoll",
            series=self.series,
        )
        self.agenda_item = AgendaItem.objects.create(
            meeting=self.meeting,
            topic=self.topic,
            working_text="Sachstand",
        )
        self.followup_item = AgendaItem.objects.create(
            meeting=self.followup_meeting,
            topic=self.topic,
            followup_of=self.agenda_item,
        )
        self.client.force_login(self.user)

    def test_draft_protocol_displays_followup_date(self):
        response = self.client.get(reverse("protocol", args=[self.meeting.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Wiedervorlage:")
        self.assertContains(response, "07.12.2026")

    def test_finalized_protocol_keeps_followup_date_in_snapshot(self):
        finalize_meeting(self.meeting)
        snapshot = self.meeting.snapshots.get(topic_id=self.topic.pk)

        self.assertEqual(snapshot.followup_date, self.followup_meeting.date)

        response = self.client.get(reverse("protocol", args=[self.meeting.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Wiedervorlage:")
        self.assertContains(response, "07.12.2026")

    def test_word_export_route_is_removed(self):
        from django.urls import NoReverseMatch, reverse

        with self.assertRaises(NoReverseMatch):
            reverse("protocol_docx")
