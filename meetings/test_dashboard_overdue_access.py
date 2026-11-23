from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import AgendaItem, Meeting, MeetingSeries, SeriesAccess, Topic


class DashboardOverdueAccessTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.reader = User.objects.create_user(
            username="overdue-reader", password="strong-test-password"
        )
        self.participant = User.objects.create_user(
            username="overdue-participant", password="strong-test-password"
        )
        self.series = MeetingSeries.objects.create(name="Überfällige Themen")
        SeriesAccess.objects.create(
            user=self.reader, series=self.series, role=SeriesAccess.ROLE_READER
        )
        SeriesAccess.objects.create(
            user=self.participant, series=self.series,
            role=SeriesAccess.ROLE_PARTICIPANT,
        )
        meeting = Meeting.objects.create(
            series=self.series, date=timezone.localdate() - timedelta(days=2)
        )
        topic = Topic.objects.create(title="Überfälliger Punkt", series=self.series)
        AgendaItem.objects.create(meeting=meeting, topic=topic, status="open")

    def test_reader_does_not_see_overdue_warning(self):
        self.client.force_login(self.reader)

        response = self.client.get(reverse("dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["overdue_count"], 0)
        self.assertNotContains(response, "überfälliges Thema")

    def test_participant_sees_overdue_warning(self):
        self.client.force_login(self.participant)

        response = self.client.get(reverse("dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["overdue_count"], 1)
        self.assertContains(response, "überfälliges Thema")
