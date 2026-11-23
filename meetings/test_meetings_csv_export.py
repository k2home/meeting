from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Meeting, MeetingSeries, SeriesAccess

User = get_user_model()


class MeetingsCsvExportTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="meeting-csv", password="test-password")
        self.series = MeetingSeries.objects.create(name="Zugängliche Reihe")
        self.private = MeetingSeries.objects.create(name="Private Reihe")
        SeriesAccess.objects.create(user=self.user, series=self.series, role=SeriesAccess.ROLE_READER)
        Meeting.objects.create(series=self.series, date=date(2026, 12, 3), title="Planung")
        Meeting.objects.create(series=self.private, date=date(2026, 12, 4), title="Vertraulich")
        self.client.force_login(self.user)

    def test_export_contains_only_accessible_meetings(self):
        response = self.client.get(reverse("meetings_csv"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv; charset=utf-8")
        content = response.content.decode("utf-8-sig")
        self.assertIn("Zugängliche Reihe", content)
        self.assertIn("Planung", content)
        self.assertNotIn("Private Reihe", content)
        self.assertNotIn("Vertraulich", content)

    def test_export_requires_login(self):
        self.client.logout()
        self.assertEqual(self.client.get(reverse("meetings_csv")).status_code, 302)
