from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Meeting, MeetingSeries, SeriesAccess

User = get_user_model()


class MeetingParticipantSearchTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="participant-search-user", password="strong-test-password"
        )
        self.series = MeetingSeries.objects.create(name="Such-Reihe")
        SeriesAccess.objects.create(user=self.user, series=self.series)
        self.meeting = Meeting.objects.create(series=self.series, date=date(2026, 12, 15))

    def test_participant_form_contains_accessible_local_search(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("meeting", args=[self.meeting.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="participant-search"')
        self.assertContains(response, 'aria-controls="participant-option-groups"')
        self.assertContains(response, 'id="participant-search-status"')
        self.assertContains(response, 'addEventListener("input"')
        self.assertContains(response, 'event.key === "Escape"')
        self.assertContains(response, 'Keine Teilnehmer gefunden.')

    def test_anonymous_user_cannot_open_participant_selection(self):
        response = self.client.get(reverse("meeting", args=[self.meeting.pk]))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)
