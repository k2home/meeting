from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import AgendaItem, Meeting, MeetingSeries, SeriesAccess, Topic

User = get_user_model()


class SeriesAgendaCompletionProgressTests(TestCase):
    def setUp(self):
        self.moderator = User.objects.create_user(
            username="series-progress", password="strong-test-password"
        )
        self.series = MeetingSeries.objects.create(name="Fortschritts-Reihe")
        SeriesAccess.objects.create(
            user=self.moderator, series=self.series, role=SeriesAccess.ROLE_MODERATOR
        )
        meeting = Meeting.objects.create(series=self.series, date=date(2026, 12, 2))
        for title, status in (
            ("Erledigt", "done"),
            ("Noch offen", "open"),
            ("In Arbeit", "in_progress"),
        ):
            topic = Topic.objects.create(title=title, series=self.series)
            AgendaItem.objects.create(meeting=meeting, topic=topic, status=status)

    def test_series_overview_calculates_completed_agenda_percentage(self):
        self.client.force_login(self.moderator)

        response = self.client.get(reverse("series_admin"))

        self.assertEqual(response.status_code, 200)
        row = next(item for item in response.context["series"] if item.pk == self.series.pk)
        self.assertEqual(row.completed_agenda_count, 1)
        self.assertEqual(row.total_agenda_count, 3)
        self.assertEqual(row.agenda_completion_percent, 33)
        self.assertContains(response, 'role="progressbar"')
