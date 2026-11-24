from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import AgendaItem, Meeting, MeetingSeries, SeriesAccess, Topic

User = get_user_model()


class MyTasksSeriesFilterTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="my-task-filter", password="test-password")
        self.first = MeetingSeries.objects.create(name="Erste Reihe")
        self.second = MeetingSeries.objects.create(name="Zweite Reihe")
        SeriesAccess.objects.create(user=self.user, series=self.first, role=SeriesAccess.ROLE_PARTICIPANT)
        SeriesAccess.objects.create(user=self.user, series=self.second, role=SeriesAccess.ROLE_PARTICIPANT)
        self.first_topic = Topic.objects.create(title="Aufgabe Erste Reihe", series=self.first, assigned_to=self.user)
        self.second_topic = Topic.objects.create(title="Aufgabe Zweite Reihe", series=self.second, assigned_to=self.user)
        today = timezone.localdate()
        for series, topic in ((self.first, self.first_topic), (self.second, self.second_topic)):
            meeting = Meeting.objects.create(series=series, date=today + timedelta(days=5))
            AgendaItem.objects.create(meeting=meeting, topic=topic, assigned_to=self.user, status="open")
        # A transferred topic may retain agenda history in another series.
        cross_series_meeting = Meeting.objects.create(
            series=self.second, date=today + timedelta(days=2),
        )
        AgendaItem.objects.create(
            meeting=cross_series_meeting, topic=self.first_topic,
            assigned_to=self.user, status="open",
        )
        self.client.force_login(self.user)

    def test_filter_limits_both_task_sections_to_selected_series(self):
        response = self.client.get(reverse("my_tasks"), {"series": self.first.pk})
        self.assertEqual(response.status_code, 200)
        self.assertEqual([topic.title for topic in response.context["main_topics"]], ["Aufgabe Erste Reihe"])
        self.assertEqual(
            response.context["main_topics"][0].next_meeting_date,
            timezone.localdate() + timedelta(days=5),
        )
        self.assertEqual(len(response.context["agenda_tasks"]), 1)
        self.assertEqual(response.context["agenda_tasks"][0].meeting.series, self.first)
        self.assertContains(response, "my-tasks-series")

    def test_invalid_or_unassigned_series_filter_is_ignored(self):
        response = self.client.get(reverse("my_tasks"), {"series": "999999"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["main_topics"]), 2)
