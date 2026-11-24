from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import MeetingSeries, SeriesAccess

User = get_user_model()


class SensitiveCsvDownloadHeadersTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username="csv-header-admin",
            email="csv-header-admin@example.test",
            password="test-password",
        )
        self.moderator = User.objects.create_user(
            username="csv-header-moderator",
            password="test-password",
        )
        self.series = MeetingSeries.objects.create(name="CSV-Export-Schutz")
        SeriesAccess.objects.create(
            user=self.moderator,
            series=self.series,
            role=SeriesAccess.ROLE_MODERATOR,
        )

    def assert_private_download(self, response):
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Cache-Control"], "private, no-store")
        self.assertIn("attachment;", response["Content-Disposition"])

    def test_user_export_is_not_cached(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse("admin:auth_user_csv_export"))
        self.assert_private_download(response)

    def test_topic_export_is_not_cached(self):
        self.client.force_login(self.moderator)
        response = self.client.get(reverse("admin:meetings_topic_csv_export"))
        self.assert_private_download(response)

    def test_audit_export_is_not_cached(self):
        self.client.force_login(self.moderator)
        response = self.client.get(reverse("audit_history_csv"))
        self.assert_private_download(response)
