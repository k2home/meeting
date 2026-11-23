from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import AuditEvent, MeetingSeries, SeriesAccess, Topic

User = get_user_model()


class AuditHistoryPaginationTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(username="audit-page-admin", email="admin@example.com", password="test-password")
        self.series = MeetingSeries.objects.create(name="Audit-Paginierung")
        self.topic = Topic.objects.create(title="Paginierungsthema", series=self.series)
        AuditEvent.objects.bulk_create([
            AuditEvent(topic=self.topic, series=self.series, action="updated", summary=f"Änderung {index}")
            for index in range(115)
        ])
        self.client.force_login(self.admin)

    def test_audit_history_is_paginated_in_pages_of_fifty(self):
        response = self.client.get(reverse("audit_history"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["events"]), 50)
        self.assertEqual(response.context["events"].paginator.count, 115)
        self.assertContains(response, "Seite 1 von 3")
        self.assertContains(response, "Ältere Einträge")

    def test_second_page_shows_older_entries(self):
        response = self.client.get(reverse("audit_history"), {"page": 2})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["events"].number, 2)
        self.assertEqual(len(response.context["events"]), 50)

    def test_invalid_page_falls_back_to_last_page(self):
        response = self.client.get(reverse("audit_history"), {"page": "999"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["events"].number, 3)
