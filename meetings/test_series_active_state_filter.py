from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import MeetingSeries, SeriesAccess

User = get_user_model()


class SeriesActiveStateFilterTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="series-state-filter", password="strong-test-password"
        )
        self.active = MeetingSeries.objects.create(name="Aktive Reihe", active=True)
        self.inactive = MeetingSeries.objects.create(name="Inaktive Reihe", active=False)
        SeriesAccess.objects.create(
            user=self.user, series=self.active, role=SeriesAccess.ROLE_MODERATOR
        )
        SeriesAccess.objects.create(
            user=self.user, series=self.inactive, role=SeriesAccess.ROLE_MODERATOR
        )

    def test_inactive_filter_shows_only_inactive_accessible_series(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("series_admin"), {"state": "inactive"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Inaktive Reihe")
        self.assertNotContains(response, "Aktive Reihe")
        self.assertEqual(response.context["selected_state"], "inactive")

    def test_invalid_state_filter_falls_back_to_all_accessible_series(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("series_admin"), {"state": "unknown"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Inaktive Reihe")
        self.assertContains(response, "Aktive Reihe")
        self.assertEqual(response.context["selected_state"], "all")
