from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import AuditEvent, MeetingSeries, Topic

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
        self.assertContains(response, 'href="?page=2"')
        self.assertContains(response, 'aria-current="page"')
        self.assertContains(response, 'aria-label="Seite 2"')

    def test_second_page_shows_older_entries_and_current_page_number(self):
        response = self.client.get(reverse("audit_history"), {"page": 2})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["events"].number, 2)
        self.assertEqual(len(response.context["events"]), 50)
        self.assertContains(response, 'aria-label="Aktuelle Seite 2"')
        self.assertContains(response, 'href="?page=1"')
        self.assertContains(response, 'href="?page=3"')

    def test_pagination_links_preserve_active_filters(self):
        response = self.client.get(reverse("audit_history"), {
            "page": 1, "series": self.series.pk, "topic": self.topic.pk,
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            f'?page=2&amp;series={self.series.pk}&amp;topic={self.topic.pk}',
        )

    def test_invalid_page_falls_back_to_last_page(self):
        response = self.client.get(reverse("audit_history"), {"page": "999"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["events"].number, 3)
        self.assertContains(response, 'aria-label="Aktuelle Seite 3"')

    def test_large_page_ranges_are_elided(self):
        AuditEvent.objects.bulk_create([
            AuditEvent(topic=self.topic, series=self.series, action="updated", summary=f"Weitere Änderung {index}")
            for index in range(500)
        ])
        response = self.client.get(reverse("audit_history"), {"page": 6})
        self.assertEqual(response.status_code, 200)
        self.assertIn("…", list(response.context["page_range"]))
        self.assertContains(response, 'aria-current="page"')
