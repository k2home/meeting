from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Meeting, MeetingSeries

User = get_user_model()


class SeriesManagementOverviewTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username="series-overview-admin",
            email="series-overview-admin@example.com",
            password="test-password",
        )
        self.client.force_login(self.admin)

    def test_overview_shows_search_status_metrics_and_meeting_actions(self):
        series = MeetingSeries.objects.create(name="Produktteam")
        today = timezone.localdate()
        completed = Meeting.objects.create(
            series=series,
            date=today - timedelta(days=7),
            finalized_at=timezone.now(),
        )
        upcoming = Meeting.objects.create(
            series=series,
            date=today + timedelta(days=7),
        )

        response = self.client.get(reverse("series_admin"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="series-overview-search"')
        self.assertContains(response, 'id="series-overview-status"')
        self.assertContains(response, 'data-series-name="produktteam"')
        self.assertContains(response, "Termine gesamt")
        self.assertContains(response, "Offen / geplant")
        self.assertContains(response, "Abgeschlossen")
        self.assertContains(response, "Reihe verwalten")
        self.assertContains(response, "Reihe bis Ende des Folgejahres verlängern")
        self.assertContains(response, reverse("meeting", args=[upcoming.pk]))
        self.assertContains(response, reverse("meeting", args=[completed.pk]))
        self.assertContains(response, "Weitere Termine anzeigen")
