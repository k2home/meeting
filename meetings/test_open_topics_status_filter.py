from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import AgendaItem, Meeting, MeetingSeries, SeriesAccess, Topic

User = get_user_model()


class OpenTopicsStatusFilterTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="open-topics-status", password="strong-test-password"
        )
        self.series = MeetingSeries.objects.create(name="Statusfilter-Reihe")
        SeriesAccess.objects.create(
            user=self.user, series=self.series, role=SeriesAccess.ROLE_MODERATOR
        )
        meeting = Meeting.objects.create(
            series=self.series, date=timezone.localdate() - timedelta(days=2)
        )
        for title, status in (
            ("Nur offen", "open"),
            ("In Bearbeitung", "in_progress"),
        ):
            topic = Topic.objects.create(title=title, series=self.series)
            AgendaItem.objects.create(meeting=meeting, topic=topic, status=status)

    def test_open_filter_limits_rows_to_open_items(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("open_topics"), {"status": "open"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Nur offen")
        self.assertNotContains(response, "In Bearbeitung")
        self.assertEqual(response.context["selected_status"], "open")

    def test_invalid_status_filter_falls_back_to_all_open_work(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("open_topics"), {"status": "invalid"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Nur offen")
        self.assertContains(response, "In Bearbeitung")
        self.assertEqual(response.context["selected_status"], "all")
