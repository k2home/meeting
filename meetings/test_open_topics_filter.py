from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import AgendaItem, Meeting, MeetingSeries, SeriesAccess, Topic

User = get_user_model()


class OpenTopicsSeriesFilterTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="open-topics-filter", password="strong-test-password"
        )
        self.first_series = MeetingSeries.objects.create(name="Erste Reihe")
        self.second_series = MeetingSeries.objects.create(name="Zweite Reihe")
        SeriesAccess.objects.create(user=self.user, series=self.first_series)
        SeriesAccess.objects.create(user=self.user, series=self.second_series)
        past_date = timezone.localdate() - timedelta(days=7)
        first_meeting = Meeting.objects.create(series=self.first_series, date=past_date)
        second_meeting = Meeting.objects.create(series=self.second_series, date=past_date)
        first_topic = Topic.objects.create(title="Thema der ersten Reihe", series=self.first_series)
        second_topic = Topic.objects.create(title="Thema der zweiten Reihe", series=self.second_series)
        AgendaItem.objects.create(meeting=first_meeting, topic=first_topic, status="open")
        AgendaItem.objects.create(meeting=second_meeting, topic=second_topic, status="open")

    def test_filter_limits_open_topics_to_selected_accessible_series(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("open_topics"), {"series": self.first_series.pk}
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Thema der ersten Reihe")
        self.assertNotContains(response, "Thema der zweiten Reihe")
        self.assertEqual(response.context["selected_series"], str(self.first_series.pk))

    def test_invalid_or_inaccessible_series_filter_falls_back_to_all_accessible_series(self):
        outsider_series = MeetingSeries.objects.create(name="Nicht zugewiesene Reihe")
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("open_topics"), {"series": outsider_series.pk}
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Thema der ersten Reihe")
        self.assertContains(response, "Thema der zweiten Reihe")
        self.assertEqual(response.context["selected_series"], "")
