from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import AgendaItem, Meeting, MeetingSeries, SeriesAccess, Topic

User = get_user_model()


class DashboardUpcomingAgendaCountTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="dashboard-agenda-count", password="strong-test-password"
        )
        self.series = MeetingSeries.objects.create(name="Dashboard-Punkte-Reihe")
        SeriesAccess.objects.create(user=self.user, series=self.series)
        self.meeting = Meeting.objects.create(
            series=self.series, date=timezone.localdate() + timedelta(days=2)
        )
        for title, status in (
            ("Offener Punkt", "open"),
            ("Punkt in Arbeit", "in_progress"),
            ("Erledigter Punkt", "done"),
        ):
            topic = Topic.objects.create(title=title, series=self.series)
            AgendaItem.objects.create(meeting=self.meeting, topic=topic, status=status)

    def test_dashboard_counts_only_open_and_in_progress_items_per_upcoming_meeting(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("dashboard"))

        self.assertEqual(response.status_code, 200)
        group = next(item for item in response.context["meeting_groups"] if item["series"] == self.series)
        self.assertEqual(group["meetings"][0].open_agenda_count, 2)
        self.assertContains(response, "2 offene Punkte")
