from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import AgendaItem, Meeting, MeetingSeries, SeriesAccess, Topic

User = get_user_model()


class MeetingAgendaStatusFilterTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="meeting-agenda-filter", password="strong-test-password"
        )
        self.series = MeetingSeries.objects.create(name="Agenda-Filter-Reihe")
        SeriesAccess.objects.create(user=self.user, series=self.series)
        self.meeting = Meeting.objects.create(series=self.series, date=date(2026, 12, 5))
        for title, status in (
            ("Offener Tagesordnungspunkt", "open"),
            ("Punkt in Bearbeitung", "in_progress"),
            ("Erledigter Tagesordnungspunkt", "done"),
        ):
            topic = Topic.objects.create(title=title, series=self.series)
            AgendaItem.objects.create(meeting=self.meeting, topic=topic, status=status)

    def test_meeting_page_offers_status_filters_and_keeps_reordering_separate(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("meeting", args=[self.meeting.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-agenda-filter="all"')
        self.assertContains(response, 'data-agenda-filter="open"')
        self.assertContains(response, 'data-agenda-filter="in_progress"')
        self.assertContains(response, 'data-agenda-filter="done"')
        self.assertContains(response, 'data-agenda-status="open"')
        self.assertContains(response, 'data-agenda-status="done"')
