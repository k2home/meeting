import csv
from io import StringIO

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import AuditEvent, MeetingSeries, SeriesAccess, Topic

User = get_user_model()


class AuditHistoryCsvExportTests(TestCase):
    def setUp(self):
        self.moderator = User.objects.create_user(username="audit-csv-moderator", password="test-password")
        self.participant = User.objects.create_user(username="audit-csv-participant", password="test-password")
        self.own_series = MeetingSeries.objects.create(name="Freigegebene Reihe")
        self.private_series = MeetingSeries.objects.create(name="Private Reihe")
        SeriesAccess.objects.create(user=self.moderator, series=self.own_series, role=SeriesAccess.ROLE_MODERATOR)
        SeriesAccess.objects.create(user=self.participant, series=self.private_series, role=SeriesAccess.ROLE_PARTICIPANT)
        self.own_topic = Topic.objects.create(title="Sichtbares Thema", series=self.own_series)
        self.private_topic = Topic.objects.create(title="Verstecktes Thema", series=self.private_series)
        AuditEvent.objects.create(topic=self.own_topic, series=self.own_series, action="created", summary="Sichtbarer Eintrag")
        AuditEvent.objects.create(topic=self.private_topic, series=self.private_series, action="created", summary="Privater Eintrag")

    def test_moderator_export_contains_only_authorized_series(self):
        self.client.force_login(self.moderator)
        response = self.client.get(reverse("audit_history_csv"))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode("utf-8-sig")
        self.assertIn("Sichtbarer Eintrag", content)
        self.assertNotIn("Privater Eintrag", content)
        self.assertIn("Freigegebene Reihe", content)

    def test_export_neutralizes_spreadsheet_formulas(self):
        AuditEvent.objects.create(
            topic=self.own_topic, series=self.own_series, action="updated",
            summary="=HYPERLINK(\"https://example.invalid\",\"Klick\")",
            changes={"Notiz": "=1+1"},
        )
        self.client.force_login(self.moderator)
        response = self.client.get(reverse("audit_history_csv"))
        rows = list(csv.reader(StringIO(response.content.decode("utf-8-sig")), delimiter=";"))
        self.assertTrue(any(row[6].startswith("'=HYPERLINK(") for row in rows[1:]))
        self.assertTrue(any(row[7] == '{"Notiz": "=1+1"}' for row in rows[1:]))

    def test_participant_cannot_export_audit_history(self):
        self.client.force_login(self.participant)
        self.assertEqual(self.client.get(reverse("audit_history_csv")).status_code, 403)

    def test_export_requires_login(self):
        response = self.client.get(reverse("audit_history_csv"))
        self.assertEqual(response.status_code, 302)
