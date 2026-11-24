from django.contrib.auth import get_user_model
from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from .models import MeetingSeries, SeriesAccess

User = get_user_model()


class UserSeriesAccessOverviewPerformanceTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username="series-overview-admin",
            email="series-overview-admin@example.test",
            password="test-password",
        )
        self.account = User.objects.create_user(
            username="series-overview-target",
            password="test-password",
        )
        self.client.force_login(self.admin)

    def test_series_assignment_overview_query_count_does_not_grow_with_series_count(self):
        first_series = MeetingSeries.objects.create(name="Reihe 1")
        SeriesAccess.objects.create(user=self.account, series=first_series, role=SeriesAccess.ROLE_READER)

        with CaptureQueriesContext(connection) as one_series_queries:
            first_response = self.client.get(reverse("management_user_series", args=[self.account.pk]))
        self.assertEqual(first_response.status_code, 200)

        for index in range(2, 7):
            series = MeetingSeries.objects.create(name=f"Reihe {index}")
            if index % 2 == 0:
                SeriesAccess.objects.create(
                    user=self.account,
                    series=series,
                    role=SeriesAccess.ROLE_MODERATOR,
                )

        with CaptureQueriesContext(connection) as many_series_queries:
            response = self.client.get(reverse("management_user_series", args=[self.account.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            len(many_series_queries),
            len(one_series_queries),
            "Die Anzahl der Datenbankabfragen darf nicht mit der Zahl der Besprechungsreihen wachsen.",
        )
