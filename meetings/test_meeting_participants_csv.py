import csv
from datetime import date
from io import StringIO

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Meeting, MeetingSeries, SeriesAccess

User = get_user_model()


class MeetingParticipantsCsvTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="csv-exporter", password="strong-test-password"
        )
        self.participant = User.objects.create_user(
            username="member", password="strong-test-password",
            first_name="Ada", last_name="Beispiel", email="ada@example.test",
        )
        self.series = MeetingSeries.objects.create(name="CSV-Reihe")
        SeriesAccess.objects.create(user=self.user, series=self.series)
        self.meeting = Meeting.objects.create(series=self.series, date=date(2026, 12, 10))
        self.meeting.participants.add(self.participant)

    def test_authorized_user_can_download_utf8_csv_with_participants(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("meeting_participants_csv", args=[self.meeting.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response["Content-Type"].startswith("text/csv"))
        self.assertIn("attachment;", response["Content-Disposition"])
        self.assertTrue(response.content.startswith(b"\xef\xbb\xbf"))
        self.assertIn("Ada".encode(), response.content)
        self.assertIn("Ada".encode(), response.content)
        self.assertNotIn("ada@example.test".encode(), response.content)

    def test_export_neutralizes_whitespace_prefixed_spreadsheet_formulas(self):
        self.participant.first_name = "=HYPERLINK(\"https://example.invalid\",\"Klick\")"
        self.participant.save(update_fields=["first_name"])
        self.client.force_login(self.user)

        response = self.client.get(reverse("meeting_participants_csv", args=[self.meeting.pk]))
        rows = list(csv.reader(StringIO(response.content.decode("utf-8-sig")), delimiter=";"))

        self.assertTrue(rows[1][0].startswith("'=HYPERLINK("))


    def test_csv_helper_neutralizes_formulas_after_leading_whitespace(self):
        from .meeting_csv import _spreadsheet_safe

        self.assertEqual(
            _spreadsheet_safe(' \t=HYPERLINK("https://example.invalid","Klick")'),
            '\' \t=HYPERLINK("https://example.invalid","Klick")',
        )

    def test_user_without_series_access_cannot_export_participants(self):
        outsider = User.objects.create_user(
            username="outsider", password="strong-test-password"
        )
        self.client.force_login(outsider)

        response = self.client.get(
            reverse("meeting_participants_csv", args=[self.meeting.pk])
        )

        self.assertEqual(response.status_code, 404)

    def test_anonymous_user_is_redirected_to_login(self):
        response = self.client.get(
            reverse("meeting_participants_csv", args=[self.meeting.pk])
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)
