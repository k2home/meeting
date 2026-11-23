from datetime import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import AuditEvent, MeetingSeries, SeriesAccess, Topic

User = get_user_model()


class AuditHistoryDateRangeTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="audit-date-filter", password="strong-test-password"
        )
        self.series = MeetingSeries.objects.create(name="Audit-Zeitraum")
        SeriesAccess.objects.create(
            user=self.user, series=self.series, role=SeriesAccess.ROLE_MODERATOR
        )
        self.topic = Topic.objects.create(title="Audit-Thema", series=self.series)
        self.early = AuditEvent.objects.create(
            topic=self.topic, actor=self.user, action="created", summary="Früher Eintrag"
        )
        self.middle = AuditEvent.objects.create(
            topic=self.topic, actor=self.user, action="updated", summary="Eintrag im Zeitraum"
        )
        self.late = AuditEvent.objects.create(
            topic=self.topic, actor=self.user, action="updated", summary="Später Eintrag"
        )
        for event, moment in (
            (self.early, datetime(2026, 1, 10, 9, 0)),
            (self.middle, datetime(2026, 2, 15, 12, 0)),
            (self.late, datetime(2026, 3, 10, 16, 0)),
        ):
            AuditEvent.objects.filter(pk=event.pk).update(
                created_at=timezone.make_aware(moment)
            )

    def test_date_range_filters_audit_entries_inclusive(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("audit_history"), {
            "start_date": "2026-02-01",
            "end_date": "2026-02-28",
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Eintrag im Zeitraum")
        self.assertNotContains(response, "Früher Eintrag")
        self.assertNotContains(response, "Später Eintrag")
        self.assertEqual(response.context["selected_start_date"], "2026-02-01")
        self.assertEqual(response.context["selected_end_date"], "2026-02-28")

    def test_reversed_dates_clear_the_date_filter(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("audit_history"), {
            "start_date": "2026-03-01",
            "end_date": "2026-02-01",
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Früher Eintrag")
        self.assertContains(response, "Eintrag im Zeitraum")
        self.assertContains(response, "Später Eintrag")
        self.assertEqual(response.context["selected_start_date"], "")
        self.assertEqual(response.context["selected_end_date"], "")
