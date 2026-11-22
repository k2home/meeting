import csv
import io

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .models import MeetingSeries, SeriesAccess, UserProfile

User = get_user_model()


class UserCsvAdminTests(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username="csv-admin", email="admin@example.com", password="test-password"
        )
        self.client.force_login(self.admin_user)

    def test_export_contains_user_fields_and_one_row_per_series(self):
        user = User.objects.create_user(
            username="csv-member", first_name="Ada", last_name="Lovelace",
            email="ada@example.com", password="test-password",
        )
        UserProfile.objects.create(user=user, short_description="01/22")
        first = MeetingSeries.objects.create(name="Vorstand")
        second = MeetingSeries.objects.create(name="Arbeitskreis IT")
        SeriesAccess.objects.create(user=user, series=first, role=SeriesAccess.ROLE_MODERATOR)
        SeriesAccess.objects.create(user=user, series=second, role=SeriesAccess.ROLE_READER)

        response = self.client.get(reverse("admin:auth_user_csv_export"))

        self.assertEqual(response.status_code, 200)
        rows = list(csv.DictReader(io.StringIO(response.content.decode("utf-8-sig")), delimiter=";"))
        member_rows = [row for row in rows if row["username"] == "csv-member"]
        self.assertEqual(len(member_rows), 2)
        self.assertEqual({row["series"] for row in member_rows}, {"Vorstand", "Arbeitskreis IT"})
        self.assertEqual({row["series_role"] for row in member_rows}, {"moderator", "reader"})
        self.assertEqual(member_rows[0]["short_description"], "01/22")
        self.assertNotIn("date_joined", member_rows[0])
        self.assertNotIn("last_login", member_rows[0])

    def test_import_preview_then_confirm_creates_user_and_multiple_series_roles(self):
        first = MeetingSeries.objects.create(name="Vorstand")
        second = MeetingSeries.objects.create(name="Arbeitskreis IT")
        csv_text = (
            "username;first_name;last_name;email;short_description;is_active;series;series_role\n"
            "ada;Ada;Lovelace;ada@example.com;01/22;true;Vorstand;moderator\n"
            "ada;Ada;Lovelace;ada@example.com;01/22;true;Arbeitskreis IT;reader\n"
        )
        upload = SimpleUploadedFile("users.csv", csv_text.encode("utf-8"), content_type="text/csv")

        preview_response = self.client.post(
            reverse("admin:auth_user_csv_import"), {"csv_file": upload}
        )

        self.assertEqual(preview_response.status_code, 200)
        self.assertEqual(preview_response.context["preview"]["users"], 1)
        self.assertFalse(User.objects.filter(username="ada").exists())
        token = preview_response.context["preview"]["token"]

        response = self.client.post(
            reverse("admin:auth_user_csv_import"),
            {"action": "confirm", "token": token},
        )

        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username="ada")
        self.assertTrue(user.has_usable_password())
        self.assertEqual(user.email, "ada@example.com")
        self.assertEqual(user.meeting_profile.short_description, "01/22")
        assignments = {
            item.series_id: item.role for item in SeriesAccess.objects.filter(user=user)
        }
        self.assertEqual(assignments, {
            first.pk: SeriesAccess.ROLE_MODERATOR,
            second.pk: SeriesAccess.ROLE_READER,
        })

    def test_import_updates_existing_user_by_email_and_replaces_series_access(self):
        user = User.objects.create_user(
            username="old-name", first_name="Old", email="same@example.com",
            password="test-password",
        )
        old_series = MeetingSeries.objects.create(name="Alt")
        new_series = MeetingSeries.objects.create(name="Neu")
        SeriesAccess.objects.create(user=user, series=old_series)

        csv_text = (
            "username;first_name;email;is_active;series;series_role\n"
            "new-name;New;same@example.com;false;Neu;participant\n"
        )
        upload = SimpleUploadedFile("users.csv", csv_text.encode("utf-8"), content_type="text/csv")
        preview = self.client.post(reverse("admin:auth_user_csv_import"), {"csv_file": upload})
        token = preview.context["preview"]["token"]
        response = self.client.post(
            reverse("admin:auth_user_csv_import"),
            {"action": "confirm", "token": token},
        )

        self.assertEqual(response.status_code, 302)
        user.refresh_from_db()
        self.assertEqual(user.username, "new-name")
        self.assertEqual(user.first_name, "New")
        self.assertFalse(user.is_active)
        self.assertEqual(
            list(SeriesAccess.objects.filter(user=user).values_list("series_id", "role")),
            [(new_series.pk, SeriesAccess.ROLE_PARTICIPANT)],
        )

    def test_unknown_series_prevents_import(self):
        csv_text = (
            "username;email;series;series_role\n"
            "ada;ada@example.com;Unbekannt;reader\n"
        )
        upload = SimpleUploadedFile("users.csv", csv_text.encode("utf-8"), content_type="text/csv")
        response = self.client.post(reverse("admin:auth_user_csv_import"), {"csv_file": upload})

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["errors"])
        self.assertFalse(User.objects.filter(username="ada").exists())

    def test_non_staff_user_cannot_access_csv_import_or_export(self):
        self.client.force_login(User.objects.create_user(username="ordinary", password="test-password"))
        self.assertEqual(self.client.get(reverse("admin:auth_user_csv_export")).status_code, 302)
        self.assertEqual(self.client.get(reverse("admin:auth_user_csv_import")).status_code, 302)
