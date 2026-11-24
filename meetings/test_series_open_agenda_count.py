from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import AgendaItem, Meeting, MeetingSeries, SeriesAccess, Topic

User = get_user_model()


class SeriesOpenAgendaCountTests(TestCase):
    def setUp(self):
        self.moderator = User.objects.create_user(
            username="series-open-count", password="strong-test-password"
        )
        self.series = MeetingSeries.objects.create(name="Offene-Punkte-Reihe")
        SeriesAccess.objects.create(
            user=self.moderator, series=self.series, role=SeriesAccess.ROLE_MODERATOR
        )
        self.meeting = Meeting.objects.create(series=self.series, date=date(2026, 12, 1))
        self.open_topic = Topic.objects.create(title="Offener Punkt", series=self.series)
        self.progress_topic = Topic.objects.create(title="Punkt in Arbeit", series=self.series)
        self.done_topic = Topic.objects.create(title="Erledigter Punkt", series=self.series)
        AgendaItem.objects.create(meeting=self.meeting, topic=self.open_topic, status="open")
        AgendaItem.objects.create(meeting=self.meeting, topic=self.progress_topic, status="in_progress")
        AgendaItem.objects.create(meeting=self.meeting, topic=self.done_topic, status="done")

    def test_series_overview_counts_open_and_in_progress_agenda_items(self):
        self.client.force_login(self.moderator)

        response = self.client.get(reverse("series_admin"))

        self.assertEqual(response.status_code, 200)
        row = next(item for item in response.context["series"] if item.pk == self.series.pk)
        self.assertEqual(row.open_agenda_count, 2)
        self.assertContains(response, "2")
        self.assertContains(response, "offene Tagesordnungspunkte")
