from datetime import date

from django.contrib.auth import get_user_model
from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.test import RequestFactory

from .models import AgendaItem, Meeting, MeetingSeries, Topic, UserProfile
from .topic_csv import export_topic_agenda_csv

User = get_user_model()


class TopicCsvExportPerformanceTests(TestCase):
    def setUp(self):
        self.series = MeetingSeries.objects.create(name="CSV-Profil-Reihe")
        self.meeting = Meeting.objects.create(series=self.series, date=date(2026, 12, 1))
        self.request = RequestFactory().get("/export.csv")

    def _create_rows(self, start, count):
        for index in range(start, start + count):
            user = User.objects.create_user(
                username=f"topic-csv-user-{index}",
                password="test-password",
            )
            UserProfile.objects.create(user=user, short_description=f"Profil {index}")
            topic = Topic.objects.create(
                title=f"CSV-Thema {index}",
                series=self.series,
                assigned_to=user,
            )
            AgendaItem.objects.create(
                meeting=self.meeting,
                topic=topic,
                assigned_to=user,
                working_text="Besprechungsnotiz",
            )

    def test_profile_queries_do_not_grow_with_exported_rows(self):
        self._create_rows(1, 1)
        with CaptureQueriesContext(connection) as one_row_queries:
            response = export_topic_agenda_csv(self.request, allowed_series_ids=[self.series.pk])
            response.content

        self._create_rows(2, 5)
        with CaptureQueriesContext(connection) as many_rows_queries:
            response = export_topic_agenda_csv(self.request, allowed_series_ids=[self.series.pk])
            response.content

        self.assertEqual(
            len(many_rows_queries),
            len(one_row_queries),
            "Die Exportabfragen dürfen nicht pro Thema oder Tagesordnungspunkt wachsen.",
        )
