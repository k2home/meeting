from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import AgendaItem, Meeting, MeetingSeries, SeriesAccess, Topic

User = get_user_model()


class ArchiveCsvExportTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="archive-csv-user", password="strong-test-password"
        )
        self.series = MeetingSeries.objects.create(name="Export-Reihe")
        self.other_series = MeetingSeries.objects.create(name="Andere Export-Reihe")
        SeriesAccess.objects.create(user=self.user, series=self.series)
        self.archived_topic = Topic.objects.create(
            title="Archiviertes Exportthema", series=self.series, status="archived"
        )
        self.formula_topic = Topic.objects.create(
            title="=2+2", series=self.series, status="archived"
        )
        self.done_meeting = Meeting.objects.create(
            series=self.series, date=date(2026, 1, 10)
        )
        self.done_topic = Topic.objects.create(
            title="Erledigtes Exportthema", series=self.series
        )
        AgendaItem.objects.create(
            meeting=self.done_meeting, topic=self.done_topic,
            status="done", working_text="Erledigter Text",
        )
        self.private_topic = Topic.objects.create(
            title="Privates Exportthema", series=self.other_series, status="archived"
        )

    def test_export_contains_only_accessible_archive_data_and_safe_csv_values(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("archive_csv_export"))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.content.startswith(b"\xef\xbb\xbf"))
        self.assertIn("Archiviertes Exportthema".encode(), response.content)
        self.assertIn("Erledigtes Exportthema".encode(), response.content)
        self.assertIn(b"'=2+2", response.content)
        self.assertNotIn("Privates Exportthema".encode(), response.content)

    def test_export_respects_selected_accessible_series(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("archive_csv_export"), {"series": self.series.pk}
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Archiviertes Exportthema".encode(), response.content)
        self.assertNotIn("Privates Exportthema".encode(), response.content)

    def test_anonymous_user_is_redirected_to_login(self):
        response = self.client.get(reverse("archive_csv_export"))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)
