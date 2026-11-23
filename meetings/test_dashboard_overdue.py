from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import AgendaItem, Meeting, MeetingSeries, SeriesAccess, Topic


class DashboardOverdueFollowupTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="dashboard-overdue-user",
            password="strong-test-password",
        )
        self.series = MeetingSeries.objects.create(name="Dashboard-Wiedervorlage")
        SeriesAccess.objects.create(
            user=self.user,
            series=self.series,
            role=SeriesAccess.ROLE_PARTICIPANT,
        )
        self.client.force_login(self.user)
        self.today = timezone.localdate()

    def _agenda_item(self, topic, meeting_date, status="open", followup_of=None):
        meeting = Meeting.objects.create(series=self.series, date=meeting_date)
        return AgendaItem.objects.create(
            meeting=meeting,
            topic=topic,
            status=status,
            followup_of=followup_of,
        )

    def _dashboard(self, **params):
        return self.client.get(reverse("dashboard"), {"assigned_to": "", **params})

    def test_old_open_item_is_overdue_without_followup(self):
        topic = Topic.objects.create(title="Nicht weitergelegt", series=self.series)
        self._agenda_item(topic, self.today - timedelta(days=2))

        response = self._dashboard(due="overdue")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["overdue_count"], 1)
        self.assertEqual(list(response.context["topics"]), [topic])
        self.assertEqual(response.context["topics"][0].next_meeting_date, self.today - timedelta(days=2))

    def test_future_followup_replaces_old_overdue_date_on_dashboard(self):
        topic = Topic.objects.create(title="Weitergelegt", series=self.series)
        source = self._agenda_item(topic, self.today - timedelta(days=5))
        followup = self._agenda_item(
            topic,
            self.today + timedelta(days=10),
            followup_of=source,
        )

        response = self._dashboard(due="future")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["overdue_count"], 0)
        self.assertEqual(list(response.context["topics"]), [topic])
        self.assertEqual(response.context["topics"][0].next_meeting_date, followup.meeting.date)

        overdue_response = self._dashboard(due="overdue")
        self.assertEqual(list(overdue_response.context["topics"]), [])

    def test_latest_completed_item_is_not_counted_as_overdue(self):
        topic = Topic.objects.create(title="Erledigt", series=self.series)
        self._agenda_item(topic, self.today - timedelta(days=5))
        self._agenda_item(
            topic,
            self.today - timedelta(days=1),
            status="done",
        )

        response = self._dashboard(status="all", due="overdue")

        self.assertEqual(response.context["overdue_count"], 0)
        self.assertEqual(list(response.context["topics"]), [])
