from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import MeetingSeries, SeriesAccess, SeriesAccessRequest


class SeriesAccessNoneRoleTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="remove-series-access", password="strong-test-password"
        )
        self.series = MeetingSeries.objects.create(name="Berechtigungsentzug")

    def test_selecting_none_removes_existing_access_immediately(self):
        SeriesAccess.objects.create(
            user=self.user, series=self.series,
            role=SeriesAccess.ROLE_PARTICIPANT,
        )
        self.client.force_login(self.user)

        response = self.client.post(reverse("user_overview"), {
            "form_type": "access_request",
            "series_id": self.series.pk,
            "role": SeriesAccess.ROLE_NONE,
        })

        self.assertRedirects(response, reverse("user_overview"))
        self.assertFalse(
            SeriesAccess.objects.filter(user=self.user, series=self.series).exists()
        )
        access_request = SeriesAccessRequest.objects.get(
            user=self.user, series=self.series
        )
        self.assertEqual(access_request.requested_role, SeriesAccess.ROLE_NONE)
        self.assertEqual(access_request.status, SeriesAccessRequest.STATUS_APPROVED)
        self.assertIsNotNone(access_request.decided_at)

    def test_selecting_none_without_existing_access_is_a_noop(self):
        self.client.force_login(self.user)

        response = self.client.post(reverse("user_overview"), {
            "form_type": "access_request",
            "series_id": self.series.pk,
            "role": SeriesAccess.ROLE_NONE,
        })

        self.assertRedirects(response, reverse("user_overview"))
        self.assertFalse(
            SeriesAccess.objects.filter(user=self.user, series=self.series).exists()
        )
        self.assertFalse(
            SeriesAccessRequest.objects.filter(user=self.user, series=self.series).exists()
        )

    def test_approved_none_request_removes_existing_access(self):
        SeriesAccess.objects.create(
            user=self.user, series=self.series,
            role=SeriesAccess.ROLE_READER,
        )
        access_request = SeriesAccessRequest.objects.create(
            user=self.user, series=self.series,
            requested_role=SeriesAccess.ROLE_NONE,
        )
        admin = get_user_model().objects.create_superuser(
            username="series-access-admin",
            email="admin@example.invalid",
            password="strong-test-password",
        )
        self.client.force_login(admin)

        response = self.client.post(reverse("series_admin"), {
            "form_type": "access_request_decision",
            "request_id": access_request.pk,
            "decision": SeriesAccessRequest.STATUS_APPROVED,
        })

        self.assertRedirects(response, reverse("series_admin"))
        self.assertFalse(
            SeriesAccess.objects.filter(user=self.user, series=self.series).exists()
        )
        access_request.refresh_from_db()
        self.assertEqual(access_request.status, SeriesAccessRequest.STATUS_APPROVED)
