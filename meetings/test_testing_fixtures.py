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

        response = self.client.post(url, {"action": "create_series", "series_count": "1", "fixture_nonce": self.client.session["testing_fixture_nonce"]})
        self.assertRedirects(response, url)
        series = MeetingSeries.objects.get()
        self.assertTrue(series.name.startswith("TEST-Besprechungsreihe "))
        self.assertTrue(SeriesAccess.objects.filter(
            user=self.admin, series=series, role=SeriesAccess.ROLE_MODERATOR
        ).exists())

        self.client.get(url)
        response = self.client.post(url, {"action": "create_users", "user_count": "2", "fixture_nonce": self.client.session["testing_fixture_nonce"]})
        self.assertRedirects(response, url)
        generated_users = User.objects.filter(username__startswith="test_fixture_")
        self.assertEqual(generated_users.count(), 2)
        self.assertTrue(all(not user.has_usable_password() for user in generated_users))
        from .models import UserProfile
        profiles = list(UserProfile.objects.filter(user__in=generated_users).select_related("user"))
        self.assertEqual(len(profiles), 2)
        short_labels = [profile.short_description for profile in profiles]
        self.assertEqual(len(set(label.split("/")[0] for label in short_labels)), 2)
        for profile in profiles:
            self.assertRegex(profile.short_description, r"^\\d{2}/\\d{2}$")
            self.assertRegex(profile.user.email, r"^[a-zäöü]+\\.[a-zäöü]+@beliebig\\.de$")
            self.assertTrue(profile.user.first_name)
            self.assertTrue(profile.user.last_name)
            self.assertEqual(profile.user.email, f"{profile.user.first_name}.{profile.user.last_name}".lower() + "@beliebig.de")

        self.client.get(url)
        response = self.client.post(url, {
            "action": "generate_meetings", "series_ids": [str(series.pk)], "fixture_nonce": self.client.session["testing_fixture_nonce"],
        })
        self.assertRedirects(response, url)
        self.assertTrue(Meeting.objects.filter(series=series).exists())

        self.client.get(url)
        response = self.client.post(url, {
            "action": "create_topics", "series_id": str(series.pk), "topic_count": "2", "fixture_nonce": self.client.session["testing_fixture_nonce"],
        })
        self.assertRedirects(response, url)
        topic = Topic.objects.filter(series=series).first()
        self.assertIsNotNone(topic)
        self.assertTrue(topic.title.startswith("TEST-"))

        self.client.get(url)
        response = self.client.post(url, {
            "action": "create_agenda_items", "topic_id": str(topic.pk), "agenda_count": "2", "fixture_nonce": self.client.session["testing_fixture_nonce"],
        })
        self.assertRedirects(response, url)
        created_items = list(AgendaItem.objects.filter(topic=topic).select_related("meeting").order_by("meeting__date"))
        self.assertEqual(len(created_items), 2)
        self.assertLess(created_items[0].meeting.date, created_items[1].meeting.date)
        self.assertIsNone(created_items[0].followup_of)
        self.assertEqual(created_items[1].followup_of, created_items[0])
        self.assertTrue(all(item.working_text for item in created_items))
        from django.utils import timezone
        self.assertTrue(Meeting.objects.filter(series=series, date__lt=timezone.localdate()).exists())
        self.assertTrue(SeriesAccess.objects.filter(
            series=series, user__username__startswith="test_fixture_"
        ).exists())


    @patch("meetings.management_views._testing_mode_enabled", return_value=True)
    def test_repeated_agenda_generation_extends_existing_followup_chain(self, _testing_mode):
        from datetime import date
        from .services import generate_meetings

        series = MeetingSeries.objects.create(
            name="TEST-Besprechungsreihe chain", recurrence="weekly", recurrence_interval=1,
            weekday=1, start_date=date(2026, 1, 1), end_date=date(2026, 3, 31),
        )
        Topic.objects.create(title="TEST-Kette", series=series)
        topic = Topic.objects.get(title="TEST-Kette")
        generate_meetings(series, include_past=True)
        url = reverse("testing_fixtures")
        self.client.get(url)
        self.client.post(url, {"action": "create_agenda_items", "topic_id": str(topic.pk), "agenda_count": "2", "fixture_nonce": self.client.session["testing_fixture_nonce"]})
        first_chain = list(AgendaItem.objects.filter(topic=topic).order_by("meeting__date", "pk"))
        self.assertEqual(len(first_chain), 2)
        self.client.get(url)
        self.client.post(url, {"action": "create_agenda_items", "topic_id": str(topic.pk), "agenda_count": "2", "fixture_nonce": self.client.session["testing_fixture_nonce"]})
        full_chain = list(AgendaItem.objects.filter(topic=topic).order_by("meeting__date", "pk"))
        self.assertEqual(len(full_chain), 4)
        self.assertIsNone(full_chain[0].followup_of)
        self.assertEqual([item.followup_of_id for item in full_chain[1:]], [item.pk for item in full_chain[:-1]])
        self.assertTrue(all(item.meeting.date.weekday() == 1 for item in full_chain))

    @patch("meetings.management_views._testing_mode_enabled", return_value=True)
    def test_reset_removes_fixture_series_meetings_topics_and_unused_users(self, _testing_mode):
        url = reverse("testing_fixtures")
        series = MeetingSeries.objects.create(
            name="TEST-Besprechungsreihe reset",
            start_date="2026-01-01", end_date="2026-12-31",
        )
        user = User.objects.create_user(username="test_fixture_reset")
        SeriesAccess.objects.create(user=user, series=series)
        topic = Topic.objects.create(title="TEST-Reset-Thema", series=series)
        meeting = Meeting.objects.create(series=series, date="2026-11-20")
        AgendaItem.objects.create(meeting=meeting, topic=topic)

        self.client.get(url)
        response = self.client.post(url, {"action": "reset_fixtures", "fixture_nonce": self.client.session["testing_fixture_nonce"]})

        self.assertRedirects(response, url)
        self.assertFalse(MeetingSeries.objects.filter(pk=series.pk).exists())
        self.assertFalse(Meeting.objects.filter(pk=meeting.pk).exists())
        self.assertFalse(Topic.objects.filter(pk=topic.pk).exists())
        self.assertFalse(User.objects.filter(pk=user.pk).exists())

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
