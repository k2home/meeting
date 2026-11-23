from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import AgendaItem, Meeting, MeetingSeries, SeriesAccess, Topic

User = get_user_model()


class DashboardNextWeekDueFilterTests(TestCase):
    def setUp(self):
        self.today = timezone.localdate()
        self.user = User.objects.create_user(
            username="next-week-user", password="strong-test-password"
        )
        self.series = MeetingSeries.objects.create(name="Nächste-Woche-Reihe")
        SeriesAccess.objects.create(user=self.user, series=self.series)
        self.client.force_login(self.user)

        self.topics = {}
        for key, offset in (
            ("today", 0),
            ("last_day", 7),
            ("outside", 8),
            ("past", -1),
        ):
            topic = Topic.objects.create(title=f"Fälligkeit {key}", series=self.series)
            meeting = Meeting.objects.create(
                series=self.series, date=self.today + timedelta(days=offset)
            )
            AgendaItem.objects.create(meeting=meeting, topic=topic, status="open")
            self.topics[key] = topic

    def test_next_week_is_the_default_and_includes_today_through_day_seven(self):
        response = self.client.get(reverse("dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["selected_due"], "next_week")
        self.assertEqual(
            set(response.context["topics"]),
            {self.topics["today"], self.topics["last_day"]},
        )
        self.assertContains(response, "Nächste Woche")

    def test_next_week_can_be_selected_explicitly(self):
        response = self.client.get(reverse("dashboard"), {"due": "next_week"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            set(response.context["topics"]),
            {self.topics["today"], self.topics["last_day"]},
        )

    def test_all_meetings_option_disables_due_date_restriction(self):
        response = self.client.get(reverse("dashboard"), {"due": ""})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            set(response.context["topics"]),
            set(self.topics.values()),
        )
