from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import AgendaItem, Meeting, MeetingSeries, SeriesAccess, Topic

User = get_user_model()


class PersonalMeetingsOverviewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="overview-user", password="test-password")
        self.other = User.objects.create_user(username="overview-other", password="test-password")
        self.participant_series = MeetingSeries.objects.create(name="Teilnehmerreihe")
        self.reader_series = MeetingSeries.objects.create(name="Leserreihe")
        self.moderator_series = MeetingSeries.objects.create(name="Moderatorreihe")
        self.private_series = MeetingSeries.objects.create(name="Fremde Reihe")
        SeriesAccess.objects.create(user=self.user, series=self.participant_series, role=SeriesAccess.ROLE_PARTICIPANT)
        SeriesAccess.objects.create(user=self.user, series=self.reader_series, role=SeriesAccess.ROLE_READER)
        SeriesAccess.objects.create(user=self.user, series=self.moderator_series, role=SeriesAccess.ROLE_MODERATOR)
        SeriesAccess.objects.create(user=self.other, series=self.private_series, role=SeriesAccess.ROLE_PARTICIPANT)
        today = timezone.localdate()
        self.past = Meeting.objects.create(series=self.participant_series, date=today - timedelta(days=7), title="Vergangene Sitzung")
        self.next_meeting = Meeting.objects.create(series=self.participant_series, date=today + timedelta(days=7), title="Nächste Sitzung")
        self.reader_meeting = Meeting.objects.create(series=self.reader_series, date=today + timedelta(days=10))
        self.moderator_meeting = Meeting.objects.create(series=self.moderator_series, date=today + timedelta(days=14))
        self.finalized_meeting = Meeting.objects.create(
            series=self.participant_series, date=today + timedelta(days=21),
            finalized_at=timezone.now(), title="Abgeschlossene Sitzung",
        )
        self.private_meeting = Meeting.objects.create(series=self.private_series, date=today + timedelta(days=2))
        topic = Topic.objects.create(title="Offener Tagesordnungspunkt", series=self.participant_series)
        AgendaItem.objects.create(meeting=self.next_meeting, topic=topic, status="open")

    def test_page_lists_only_meetings_from_series_with_user_access(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("meetings_overview"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Teilnehmerreihe")
        self.assertContains(response, "Leserreihe")
        self.assertContains(response, "Moderatorreihe")
        self.assertNotContains(response, "Fremde Reihe")
        self.assertContains(response, "Vergangene Sitzung")
        self.assertContains(response, "calendar-show-past")
        self.assertContains(response, "calendar-hide-finalized")

    def test_completed_toggle_starts_disabled_and_calendar_marks_finalized_events(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("meetings_overview"))
        self.assertContains(response, 'id="calendar-hide-finalized"')
        event_by_id = {
            event["id"]: event for event in response.context["calendar_events"]
        }
        self.assertFalse(event_by_id[self.next_meeting.pk]["finalized"])
        self.assertTrue(event_by_id[self.finalized_meeting.pk]["finalized"])

    def test_series_table_shows_next_open_meeting_and_role(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("meetings_overview"))
        self.assertContains(response, "Nächste Sitzung")
        self.assertContains(response, "Teilnehmer")
        self.assertContains(response, "Leser")
        self.assertContains(response, "Moderator")
        self.assertContains(response, "Offene Tagesordnungspunkte")
        self.assertContains(response, "1")

    def test_reader_role_is_included_without_meeting_participant_membership(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("meetings_overview"))
        self.assertContains(response, str(self.reader_meeting.pk))

    def test_unauthenticated_user_is_redirected_to_login(self):
        response = self.client.get(reverse("meetings_overview"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)
