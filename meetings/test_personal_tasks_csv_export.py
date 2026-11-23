from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import AgendaItem, Meeting, MeetingSeries, SeriesAccess, Topic

User = get_user_model()


class PersonalTasksCsvExportTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="task-csv-user", password="test-password")
        self.other = User.objects.create_user(username="task-csv-other", password="test-password")
        self.series = MeetingSeries.objects.create(name="Eigene Reihe")
        self.private_series = MeetingSeries.objects.create(name="Fremde Reihe")
        SeriesAccess.objects.create(user=self.user, series=self.series, role=SeriesAccess.ROLE_PARTICIPANT)
        SeriesAccess.objects.create(user=self.other, series=self.private_series, role=SeriesAccess.ROLE_PARTICIPANT)
        self.topic = Topic.objects.create(title="Meine Hauptaufgabe", series=self.series, assigned_to=self.user)
        self.private_topic = Topic.objects.create(title="Fremde Aufgabe", series=self.private_series, assigned_to=self.user)
        meeting = Meeting.objects.create(series=self.series, date=timezone.localdate() + timedelta(days=5))
        AgendaItem.objects.create(meeting=meeting, topic=self.topic, assigned_to=self.user, working_text="Vorbereiten")
        private_meeting = Meeting.objects.create(series=self.private_series, date=timezone.localdate() + timedelta(days=6))
        AgendaItem.objects.create(meeting=private_meeting, topic=self.private_topic, assigned_to=self.user, working_text="Privat")
        self.client.force_login(self.user)

    def test_export_contains_only_accessible_personal_tasks(self):
        response = self.client.get(reverse("personal_tasks_csv"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv; charset=utf-8")
        content = response.content.decode("utf-8-sig")
        self.assertIn("Meine Hauptaufgabe", content)
        self.assertIn("Vorbereiten", content)
        self.assertNotIn("Fremde Aufgabe", content)
        self.assertNotIn("Privat", content)

    def test_export_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse("personal_tasks_csv"))
        self.assertEqual(response.status_code, 302)
