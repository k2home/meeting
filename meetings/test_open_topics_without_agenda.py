from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import AgendaItem, Meeting, MeetingSeries, SeriesAccess, Topic


class OpenTopicsWithoutAgendaItemTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="open-topics-user",
            password="strong-test-password",
        )
        self.series = MeetingSeries.objects.create(name="Offene-Punkte-Reihe")
        SeriesAccess.objects.create(
            user=self.user,
            series=self.series,
            role=SeriesAccess.ROLE_PARTICIPANT,
        )
        self.client.force_login(self.user)
        self.today = timezone.localdate()

    def test_active_topic_without_any_agenda_item_is_shown(self):
        topic = Topic.objects.create(
            title="Noch nie auf der Tagesordnung",
            series=self.series,
            status="open",
        )

        response = self.client.get(reverse("open_topics"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, topic.title)
        self.assertContains(response, "Bisher noch nicht auf einer Tagesordnung geführt.")
        self.assertEqual(len(response.context["rows"]), 1)
        self.assertIsNone(response.context["rows"][0]["item"])
        self.assertEqual(response.context["rows"][0]["topic"], topic)

    def test_topic_without_agenda_item_can_be_added_to_future_meeting(self):
        topic = Topic.objects.create(
            title="Erster Tagesordnungspunkt",
            series=self.series,
            status="in_progress",
        )
        meeting = Meeting.objects.create(
            series=self.series,
            date=self.today + timedelta(days=7),
        )

        response = self.client.post(
            reverse("open_topics"),
            {"schedule_topic": topic.pk, "target_meeting": meeting.pk},
        )

        self.assertRedirects(response, reverse("open_topics"))
        item = AgendaItem.objects.get(topic=topic, meeting=meeting)
        self.assertEqual(item.status, "in_progress")
        self.assertEqual(item.working_text, "")
        self.assertFalse(item.carried_forward)
        self.assertIsNone(item.followup_of)

    def test_completed_or_archived_topics_without_agenda_items_are_not_shown(self):
        Topic.objects.create(
            title="Erledigt",
            series=self.series,
            status="done",
        )
        Topic.objects.create(
            title="Archiviert",
            series=self.series,
            status="archived",
        )

        response = self.client.get(reverse("open_topics"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["rows"], [])
