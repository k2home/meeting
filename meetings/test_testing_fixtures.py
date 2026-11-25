from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import AgendaItem, Meeting, MeetingSeries, SeriesAccess, Topic


User = get_user_model()


class TestingFixtureViewTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username="testing-admin", email="testing-admin@example.invalid",
            password="strong-test-password",
        )
        self.client.force_login(self.admin)

    @patch("meetings.management_views._testing_mode_enabled", return_value=True)
    def test_all_fixture_actions_can_be_started_independently(self, _testing_mode):
        url = reverse("testing_fixtures")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Besprechungsserien anlegen")
        self.assertContains(response, "Termine für Serien generieren")

        response = self.client.post(url, {"action": "create_series", "series_count": "1"})
        self.assertRedirects(response, url)
        series = MeetingSeries.objects.get()
        self.assertTrue(series.name.startswith("TEST-Besprechungsreihe "))
        self.assertTrue(SeriesAccess.objects.filter(
            user=self.admin, series=series, role=SeriesAccess.ROLE_MODERATOR
        ).exists())

        response = self.client.post(url, {
            "action": "generate_meetings", "series_ids": [str(series.pk)],
        })
        self.assertRedirects(response, url)
        self.assertTrue(Meeting.objects.filter(series=series).exists())

        response = self.client.post(url, {
            "action": "create_topics", "series_id": str(series.pk), "topic_count": "2",
        })
        self.assertRedirects(response, url)
        topic = Topic.objects.filter(series=series).first()
        self.assertIsNotNone(topic)
        self.assertTrue(topic.title.startswith("TEST-"))

        response = self.client.post(url, {
            "action": "create_agenda_items", "topic_id": str(topic.pk), "agenda_count": "2",
        })
        self.assertRedirects(response, url)
        self.assertGreaterEqual(AgendaItem.objects.filter(topic=topic).count(), 1)

        response = self.client.post(url, {"action": "create_users", "user_count": "2"})
        self.assertRedirects(response, url)
        generated_users = User.objects.filter(username__startswith="test_")
        self.assertEqual(generated_users.count(), 2)
        self.assertTrue(all(not user.has_usable_password() for user in generated_users))

    @patch("meetings.management_views._testing_mode_enabled", return_value=False)
    def test_fixture_page_is_unavailable_outside_testing_mode(self, _testing_mode):
        response = self.client.get(reverse("testing_fixtures"))
        self.assertEqual(response.status_code, 404)

    @patch("meetings.management_views._testing_mode_enabled", return_value=True)
    def test_fixture_page_requires_global_admin(self, _testing_mode):
        member = User.objects.create_user(username="ordinary-member", password="strong-test-password")
        self.client.force_login(member)
        response = self.client.get(reverse("testing_fixtures"))
        self.assertEqual(response.status_code, 403)
