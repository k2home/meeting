from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import MeetingSeries, SeriesAccess

User = get_user_model()


class GroupMembershipRoleSummaryTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username="group-summary-admin", email="group-summary@example.test",
            password="strong-test-password",
        )
        self.series = MeetingSeries.objects.create(name="Mitgliederübersicht")
        for username, role in (
            ("summary-moderator", SeriesAccess.ROLE_MODERATOR),
            ("summary-member", SeriesAccess.ROLE_PARTICIPANT),
            ("summary-reader", SeriesAccess.ROLE_READER),
        ):
            user = User.objects.create_user(username=username, password="strong-test-password")
            SeriesAccess.objects.create(user=user, series=self.series, role=role)

    def test_group_overview_counts_members_by_role(self):
        self.client.force_login(self.admin)

        response = self.client.get(reverse("management_groups"))

        self.assertEqual(response.status_code, 200)
        row = next(item for item in response.context["series_rows"] if item["series"].pk == self.series.pk)
        self.assertEqual(row["member_count"], 3)
        self.assertEqual(row["role_counts"][SeriesAccess.ROLE_MODERATOR], 1)
        self.assertEqual(row["role_counts"][SeriesAccess.ROLE_PARTICIPANT], 1)
        self.assertEqual(row["role_counts"][SeriesAccess.ROLE_READER], 1)
