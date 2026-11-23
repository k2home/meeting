from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Meeting, MeetingSeries, SeriesAccess

User = get_user_model()


class MeetingCalendarListViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="calendar-list-user", password="strong-test-password"
        )
        self.series = MeetingSeries.objects.create(name="Listenansicht-Reihe")
        SeriesAccess.objects.create(user=self.user, series=self.series)
        self.meeting = Meeting.objects.create(
            series=self.series,
            date=timezone.localdate() + timedelta(days=2),
            title="Termin in Listenansicht",
        )

    def test_meetings_calendar_offers_accessible_list_view(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("meetings_overview"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-calendar-view="list"')
        self.assertContains(response, "calendar-list-item")
        self.assertContains(response, "Termin in Listenansicht")
        self.assertContains(response, 'const hideFinalized = document.getElementById("calendar-hide-finalized")')
        self.assertContains(response, 'hideFinalized?.checked')
