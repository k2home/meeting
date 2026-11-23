from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import AgendaItem, Meeting, MeetingSeries, SeriesAccess, Topic

User = get_user_model()


class ArchiveSeriesFilterTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="archive-filter-user", password="strong-test-password"
        )
        self.first_series = MeetingSeries.objects.create(name="Archiv Reihe A")
        self.second_series = MeetingSeries.objects.create(name="Archiv Reihe B")
        SeriesAccess.objects.create(user=self.user, series=self.first_series)
        SeriesAccess.objects.create(user=self.user, series=self.second_series)
        self.first_topic = Topic.objects.create(
            title="Archiviertes Thema A", series=self.first_series, status="archived"
        )
        self.second_topic = Topic.objects.create(
            title="Archiviertes Thema B", series=self.second_series, status="archived"
        )
        first_meeting = Meeting.objects.create(series=self.first_series, date=date(2026, 1, 5))
        second_meeting = Meeting.objects.create(series=self.second_series, date=date(2026, 1, 6))
        first_done = Topic.objects.create(title="Erledigter Punkt A", series=self.first_series)
        second_done = Topic.objects.create(title="Erledigter Punkt B", series=self.second_series)
        AgendaItem.objects.create(meeting=first_meeting, topic=first_done, status="done")
        AgendaItem.objects.create(meeting=second_meeting, topic=second_done, status="done")

    def test_series_filter_applies_to_archived_topics_and_completed_agenda_items(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("archive"), {"series": self.first_series.pk}
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Archiviertes Thema A")
        self.assertContains(response, "Erledigter Punkt A")
        self.assertNotContains(response, "Archiviertes Thema B")
        self.assertNotContains(response, "Erledigter Punkt B")

    def test_inaccessible_series_id_does_not_expose_other_series(self):
        outsider_series = MeetingSeries.objects.create(name="Nicht zugängliche Reihe")
        outsider_topic = Topic.objects.create(
            title="Fremdes Archivthema", series=outsider_series, status="archived"
        )
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("archive"), {"series": outsider_series.pk}
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Fremdes Archivthema")
        self.assertContains(response, "Archiviertes Thema A")
        self.assertContains(response, "Archiviertes Thema B")
        self.assertEqual(response.context["selected_series"], "")
        visible_series_ids = set(response.context["series_choices"].values_list("pk", flat=True))
        self.assertNotIn(outsider_series.pk, visible_series_ids)
