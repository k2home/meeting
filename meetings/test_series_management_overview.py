from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Meeting, MeetingSeries

User = get_user_model()


class SeriesManagementOverviewTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username="series-overview-admin",
            email="series-overview-admin@example.com",
            password="test-password",
        )
        self.client.force_login(self.admin)

    def test_overview_shows_search_status_metrics_and_meeting_actions(self):
        series = MeetingSeries.objects.create(name="Produktteam")
        today = timezone.localdate()
        completed = Meeting.objects.create(
            series=series,
            date=today - timedelta(days=7),
            finalized_at=timezone.now(),
        )
        upcoming = Meeting.objects.create(
            series=series,
            date=today + timedelta(days=7),
        )

        response = self.client.get(reverse("series_admin"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="series-overview-search"')
        self.assertContains(response, 'id="series-overview-status"')
        self.assertContains(response, 'data-series-name="produktteam"')
        self.assertContains(response, "Termine gesamt")
        self.assertContains(response, "Offen / geplant")
        self.assertContains(response, "Abgeschlossen")
        self.assertContains(response, "Reihe verwalten")
        self.assertContains(response, "Reihe bis Ende des Folgejahres verlängern")
        self.assertContains(response, reverse("meeting", args=[upcoming.pk]))
        self.assertContains(response, reverse("meeting", args=[completed.pk]))
        self.assertContains(response, "Weitere Termine anzeigen")


    def test_deleting_series_archives_topics_and_keeps_meetings_in_archive(self):
        from .models import Topic

        series = MeetingSeries.objects.create(name="Archivteam")
        meeting = Meeting.objects.create(series=series, date=timezone.localdate() - timedelta(days=2))
        topic = Topic.objects.create(series=series, title="Archivpunkt")

        response = self.client.post(reverse("series_delete", args=[series.pk]))

        self.assertEqual(response.status_code, 302)
        self.assertFalse(MeetingSeries.objects.filter(pk=series.pk).exists())
        meeting.refresh_from_db()
        topic.refresh_from_db()
        self.assertIsNone(meeting.series_id)
        self.assertEqual(meeting.archived_series_name, "Archivteam")
        self.assertEqual(topic.status, "archived")
        self.assertIsNone(topic.series_id)

    def test_deleting_future_meetings_removes_future_agenda_items(self):
        from .models import AgendaItem, Topic

        series = MeetingSeries.objects.create(name="Zukunftsteam")
        today = timezone.localdate()
        past = Meeting.objects.create(series=series, date=today - timedelta(days=1))
        future = Meeting.objects.create(series=series, date=today + timedelta(days=1))
        past_topic = Topic.objects.create(series=series, title="Vergangener Punkt")
        future_topic = Topic.objects.create(series=series, title="Zukünftiger Punkt")
        AgendaItem.objects.create(meeting=past, topic=past_topic)
        AgendaItem.objects.create(meeting=future, topic=future_topic)

        response = self.client.post(reverse("series_delete_future", args=[series.pk]))

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Meeting.objects.filter(pk=past.pk).exists())
        self.assertFalse(Meeting.objects.filter(pk=future.pk).exists())
        self.assertTrue(AgendaItem.objects.filter(meeting=past, topic=past_topic).exists())
        self.assertFalse(AgendaItem.objects.filter(topic=future_topic).exists())
        future_topic.refresh_from_db()
        self.assertEqual(future_topic.status, "archived")
        self.assertIsNone(future_topic.series_id)
