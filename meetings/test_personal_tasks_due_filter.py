from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import AgendaItem, Meeting, MeetingSeries, SeriesAccess, Topic

User = get_user_model()


class PersonalTasksDueFilterTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="task-due-filter", password="strong-test-password"
        )
        self.series = MeetingSeries.objects.create(name="Aufgabenfilter-Reihe")
        SeriesAccess.objects.create(user=self.user, series=self.series)
        today = timezone.localdate()
        dates = {
            "overdue": today - timedelta(days=3),
            "today": today,
            "upcoming": today + timedelta(days=5),
        }
        for kind, meeting_date in dates.items():
            meeting = Meeting.objects.create(series=self.series, date=meeting_date)
            topic = Topic.objects.create(
                title=f"Aufgabe {kind}", series=self.series, assigned_to=self.user
            )
            AgendaItem.objects.create(meeting=meeting, topic=topic, status="open")
        self.no_meeting = Topic.objects.create(
            title="Aufgabe ohne Termin", series=self.series, assigned_to=self.user
        )

    def test_overdue_filter_only_shows_overdue_main_topics(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("my_tasks"), {"due": "overdue"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Aufgabe overdue")
        self.assertNotContains(response, "Aufgabe today")
        self.assertNotContains(response, "Aufgabe upcoming")
        self.assertEqual(response.context["selected_due"], "overdue")

    def test_without_meeting_filter_shows_topics_without_planned_meetings(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("my_tasks"), {"due": "without_meeting"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Aufgabe ohne Termin")
        self.assertNotContains(response, "Aufgabe overdue")
        self.assertNotContains(response, "Aufgabe today")

    def test_today_filter_includes_topics_due_today(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("my_tasks"), {"due": "today"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Aufgabe today")
        self.assertNotContains(response, "Aufgabe overdue")
