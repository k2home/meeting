from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import MeetingSeries, SeriesAccess, SeriesAccessRequest

User = get_user_model()


class SeriesAccessRequestSearchTests(TestCase):
    def setUp(self):
        self.moderator = User.objects.create_user(
            username="request-search-moderator", password="strong-test-password"
        )
        self.applicant = User.objects.create_user(
            username="search-applicant", password="strong-test-password",
            first_name="Lena", last_name="Beispiel",
        )
        self.series = MeetingSeries.objects.create(name="Suchbare Reihe")
        SeriesAccess.objects.create(
            user=self.moderator, series=self.series, role=SeriesAccess.ROLE_MODERATOR
        )
        SeriesAccessRequest.objects.create(
            user=self.applicant, series=self.series,
            requested_role=SeriesAccess.ROLE_PARTICIPANT,
        )

    def test_pending_access_requests_include_local_search(self):
        self.client.force_login(self.moderator)

        response = self.client.get(reverse("series_admin"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="access-request-search"')
        self.assertContains(response, 'aria-controls="access-request-table"')
        self.assertContains(response, "search-applicant")
        self.assertContains(response, "Suchbare Reihe")
