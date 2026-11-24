from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import AgendaItem, Meeting, MeetingSeries, SeriesAccess, Topic

User = get_user_model()


class DashboardDateRangeFilterTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="date-range-user", password="test-password")
        self.series = MeetingSeries.objects.create(name="Datumsfilter-Reihe")
        SeriesAccess.objects.create(user=self.user, series=self.series, role=SeriesAccess.ROLE_PARTICIPANT)
        self.near_topic = Topic.objects.create(title="Termin im Bereich", series=self.series)
        self.far_topic = Topic.objects.create(title="Termin außerhalb", series=self.series)
        today = timezone.localdate()
        near = Meeting.objects.create(series=self.series, date=today + timedelta(days=4))
        far = Meeting.objects.create(series=self.series, date=today + timedelta(days=20))
        AgendaItem.objects.create(meeting=near, topic=self.near_topic, status="open")
        AgendaItem.objects.create(meeting=far, topic=self.far_topic, status="open", assigned_to=self.user)
        self.client.force_login(self.user)

    def test_dashboard_filters_by_custom_meeting_date_range(self):
        today = timezone.localdate()
        response = self.client.get(reverse("dashboard"), {
            "from_date": (today + timedelta(days=2)).isoformat(),
            "to_date": (today + timedelta(days=8)).isoformat(),
            "assigned_to": "",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Termin im Bereich")
        self.assertNotContains(response, "Termin außerhalb")
        self.assertEqual(response.context["selected_due"], "")

    def test_single_date_bound_can_be_used_and_invalid_other_bound_is_discarded(self):
        today = timezone.localdate()
        upper_bound = (today + timedelta(days=10)).isoformat()
        response = self.client.get(reverse("dashboard"), {
            "from_date": "kein-datum", "to_date": upper_bound, "assigned_to": "",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Termin im Bereich")
        self.assertNotContains(response, "Termin außerhalb")
        self.assertEqual(response.context["selected_from_date"], "")
        self.assertEqual(response.context["selected_to_date"], upper_bound)

    def test_reversed_date_range_is_discarded(self):
        today = timezone.localdate()
        response = self.client.get(reverse("dashboard"), {
            "from_date": (today + timedelta(days=10)).isoformat(),
            "to_date": (today + timedelta(days=2)).isoformat(),
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["selected_from_date"], "")
        self.assertEqual(response.context["selected_to_date"], "")
        self.assertEqual(response.context["selected_due"], "next_week")
