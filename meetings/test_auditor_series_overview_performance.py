from django.contrib.auth import get_user_model
from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from .models import MeetingSeries, SeriesAccess
from .user_roles import sync_user_role

User = get_user_model()


class AuditorSeriesOverviewPerformanceTests(TestCase):
    def setUp(self):
        self.auditor = User.objects.create_user(
            username="series-auditor",
            password="test-password",
        )
        sync_user_role(self.auditor, "auditor")
        self.member = User.objects.create_user(
            username="series-auditor-member",
            password="test-password",
        )
        self.client.force_login(self.auditor)

    def test_auditor_group_overview_query_count_does_not_grow_with_series_count(self):
        first_series = MeetingSeries.objects.create(name="Auditor-Reihe 1")
        SeriesAccess.objects.create(
            user=self.member,
            series=first_series,
            role=SeriesAccess.ROLE_READER,
        )

        with CaptureQueriesContext(connection) as one_series_queries:
            first_response = self.client.get(reverse("auditor_groups"))
        self.assertEqual(first_response.status_code, 200)

        for index in range(2, 7):
            series = MeetingSeries.objects.create(name=f"Auditor-Reihe {index}")
            SeriesAccess.objects.create(
                user=self.member,
                series=series,
                role=SeriesAccess.ROLE_MODERATOR if index % 2 == 0 else SeriesAccess.ROLE_READER,
            )

        with CaptureQueriesContext(connection) as many_series_queries:
            response = self.client.get(reverse("auditor_groups"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            len(many_series_queries),
            len(one_series_queries),
            "Die Anzahl der Datenbankabfragen darf nicht mit der Zahl der Besprechungsreihen wachsen.",
        )
