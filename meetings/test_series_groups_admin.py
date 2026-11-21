from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from meetings.models import MeetingSeries, SeriesAccess

User = get_user_model()


class SeriesGroupsAdminTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username="groups-admin", email="admin@example.com", password="test-password"
        )
        self.client.force_login(self.admin)
        self.series = MeetingSeries.objects.create(name="Vorstand")
        self.empty_series = MeetingSeries.objects.create(name="Arbeitskreis IT")
        self.member = User.objects.create_user(
            username="ada", first_name="Ada", last_name="Lovelace", password="test-password"
        )
        self.access = SeriesAccess.objects.create(
            user=self.member, series=self.series, role=SeriesAccess.ROLE_READER
        )

    def test_groups_page_lists_every_series_and_existing_member_role(self):
        response = self.client.get(reverse("admin:auth_group_changelist"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Vorstand")
        self.assertContains(response, "Arbeitskreis IT")
        self.assertContains(response, "Ada Lovelace")
        self.assertContains(response, "Leser*in")

    def test_group_page_can_add_a_user_to_a_series(self):
        response = self.client.post(reverse("admin:auth_group_changelist"), {
            "action": "add",
            "series_id": self.series.pk,
            "user_id": self.admin.pk,
            "role": SeriesAccess.ROLE_MODERATOR,
        })

        self.assertEqual(response.status_code, 302)
        access = SeriesAccess.objects.get(series=self.series, user=self.admin)
        self.assertEqual(access.role, SeriesAccess.ROLE_MODERATOR)

    def test_group_page_can_change_a_series_role(self):
        response = self.client.post(reverse("admin:auth_group_changelist"), {
            "action": "update",
            "access_id": self.access.pk,
            "role": SeriesAccess.ROLE_MODERATOR,
        })

        self.assertEqual(response.status_code, 302)
        self.access.refresh_from_db()
        self.assertEqual(self.access.role, SeriesAccess.ROLE_MODERATOR)

    def test_group_page_can_remove_a_user_from_a_series(self):
        response = self.client.post(reverse("admin:auth_group_changelist"), {
            "action": "remove",
            "access_id": self.access.pk,
        })

        self.assertEqual(response.status_code, 302)
        self.assertFalse(SeriesAccess.objects.filter(pk=self.access.pk).exists())

    def test_non_admin_cannot_change_group_memberships(self):
        ordinary = User.objects.create_user(username="ordinary", password="test-password")
        self.client.force_login(ordinary)

        response = self.client.post(reverse("admin:auth_group_changelist"), {
            "action": "add",
            "series_id": self.series.pk,
            "user_id": ordinary.pk,
            "role": SeriesAccess.ROLE_PARTICIPANT,
        })

        self.assertEqual(response.status_code, 302)
        self.assertFalse(SeriesAccess.objects.filter(series=self.series, user=ordinary).exists())
