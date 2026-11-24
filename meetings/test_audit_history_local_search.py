from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import AuditEvent, MeetingSeries, SeriesAccess, Topic

User = get_user_model()


class AuditHistoryLocalSearchTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="audit-local-search", password="strong-test-password"
        )
        self.series = MeetingSeries.objects.create(name="Audit-Suchreihe")
        SeriesAccess.objects.create(
            user=self.user, series=self.series, role=SeriesAccess.ROLE_MODERATOR
        )
        self.topic = Topic.objects.create(title="Audit-Suchthema", series=self.series)
        AuditEvent.objects.create(
            topic=self.topic, actor=self.user, action="updated",
            summary="Budgetfreigabe wurde angepasst",
        )

    def test_audit_history_contains_accessible_local_search(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("audit_history"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="audit-local-search-input"')
        self.assertContains(response, 'aria-controls="audit-history-entries"')
        self.assertContains(response, "Budgetfreigabe wurde angepasst")
        self.assertContains(response, "audit-entry")
        self.assertContains(response, 'aria-live="polite"')
