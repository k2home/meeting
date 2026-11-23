from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import ArchivedMeetingAccess, Meeting, MeetingSeries, SeriesAccess

User = get_user_model()


class CalendarExportTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="calendar-user", password="test-password")
        self.visible = MeetingSeries.objects.create(name="Sichtbare Reihe")
        self.hidden = MeetingSeries.objects.create(name="Vertrauliche Reihe")
        SeriesAccess.objects.create(user=self.user, series=self.visible, role=SeriesAccess.ROLE_READER)
        Meeting.objects.create(series=self.visible, date=date(2026, 12, 1), title="Planung,;Überblick")
        Meeting.objects.create(series=self.hidden, date=date(2026, 12, 2), title="Geheim")
        archived = Meeting.objects.create(
            series=None, archived_series_name="Ehemalige Reihe",
            date=date(2026, 12, 3), title="Archivierter Termin",
        )
        ArchivedMeetingAccess.objects.create(meeting=archived, user=self.user, role="reader")

    def test_export_requires_login(self):
        response = self.client.get(reverse("calendar_export"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_export_is_access_scoped_and_escapes_text(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("calendar_export"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/calendar; charset=utf-8")
        self.assertIn('attachment; filename="meeting-manager.ics"', response["Content-Disposition"])
        content = response.content.decode("utf-8")
        self.assertIn(r"SUMMARY:Planung\,\;Überblick", content)
        self.assertIn("DESCRIPTION:Sichtbare Reihe", content)
        self.assertIn("SUMMARY:Archivierter Termin", content)
        self.assertIn("DESCRIPTION:Ehemalige Reihe", content)
        self.assertNotIn("Vertrauliche Reihe", content)
        self.assertNotIn("Geheim", content)
        self.assertIn("DTSTART;VALUE=DATE:20261201", content)
        self.assertIn("DTEND;VALUE=DATE:20261202", content)
        self.assertIn("DTSTART;VALUE=DATE:20261203", content)
        self.assertTrue(content.endswith("END:VCALENDAR\r\n"))

    def test_administrator_can_export_all_series(self):
        self.user.is_superuser = True
        self.user.save(update_fields=["is_superuser"])
        self.client.force_login(self.user)
        response = self.client.get(reverse("calendar_export"))
        self.assertIn("Geheim", response.content.decode("utf-8"))
