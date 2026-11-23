from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Meeting, MeetingSeries, SeriesAccess

User = get_user_model()


class MeetingCalendarRoleFilterTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="calendar-role-filter", password="strong-test-password"
        )
        self.participant_series = MeetingSeries.objects.create(name="Teilnehmer-Reihe")
        self.moderator_series = MeetingSeries.objects.create(name="Moderator-Reihe")
        SeriesAccess.objects.create(user=self.user, series=self.participant_series)
        SeriesAccess.objects.create(
            user=self.user, series=self.moderator_series,
            role=SeriesAccess.ROLE_MODERATOR,
        )
        Meeting.objects.create(
            series=self.participant_series,
            date=timezone.localdate() + timedelta(days=2),
        )
        Meeting.objects.create(
            series=self.moderator_series,
            date=timezone.localdate() + timedelta(days=3),
        )

    def test_calendar_offers_role_filter_for_existing_access_roles(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("meetings_overview"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="calendar-role-filter"')
        self.assertContains(response, '<option value="Moderator">Moderator</option>')
        self.assertContains(response, '<option value="Teilnehmer">Teilnehmer</option>')
        self.assertEqual(
            {event["role"] for event in response.context["calendar_events"]},
            {"Teilnehmer", "Moderator"},
        )
