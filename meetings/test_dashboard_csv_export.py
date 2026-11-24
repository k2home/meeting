from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import AgendaItem, Meeting, MeetingSeries, SeriesAccess, Topic

User = get_user_model()


class FilteredDashboardCsvExportTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="dashboard-csv-user", password="strong-test-password"
        )
        self.series = MeetingSeries.objects.create(name="Dashboard-Export-Reihe")
        self.hidden_series = MeetingSeries.objects.create(name="Private Dashboard-Reihe")
        SeriesAccess.objects.create(user=self.user, series=self.series)
        today = timezone.localdate()
        meeting = Meeting.objects.create(
            series=self.series, date=today + timedelta(days=3)
        )
        visible = Topic.objects.create(
            title="=1+1", series=self.series, assigned_to=self.user
        )
        AgendaItem.objects.create(meeting=meeting, topic=visible, status="open", assigned_to=self.user)
        hidden = Topic.objects.create(
            title="Nicht exportieren", series=self.hidden_series
        )
        hidden_meeting = Meeting.objects.create(
            series=self.hidden_series, date=today + timedelta(days=4)
        )
        AgendaItem.objects.create(meeting=hidden_meeting, topic=hidden, status="open")

    def test_csv_export_uses_dashboard_filters_and_access_scope(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("dashboard"), {
            "q": "1+1", "due": "", "export": "csv",
        })

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response["Content-Type"].startswith("text/csv"))
        self.assertTrue(response.content.startswith(b"\xef\xbb\xbf"))
        self.assertIn(b"'=1+1", response.content)
        self.assertIn("Dashboard-Export-Reihe".encode(), response.content)
        self.assertNotIn("Nicht exportieren".encode(), response.content)

    def test_regular_dashboard_request_still_renders_html(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("dashboard"), {"due": ""})

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response["Content-Type"].startswith("text/html"))
