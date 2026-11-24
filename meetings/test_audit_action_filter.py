from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import AuditEvent, MeetingSeries, SeriesAccess, Topic

User = get_user_model()


class AuditActionFilterTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="audit-filter", password="test-password")
        self.series = MeetingSeries.objects.create(name="Filterreihe")
        SeriesAccess.objects.create(user=self.user, series=self.series, role=SeriesAccess.ROLE_MODERATOR)
        self.topic = Topic.objects.create(title="Filterthema", series=self.series)
        AuditEvent.objects.create(topic=self.topic, series=self.series, actor=self.user, action="created", summary="Thema angelegt")
        AuditEvent.objects.create(topic=self.topic, series=self.series, actor=self.user, action="updated", summary="Thema geändert")
        self.client.force_login(self.user)

    def test_action_filter_limits_events_to_selected_action(self):
        response = self.client.get(reverse("audit_history"), {"action": "created"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context["events"]), [AuditEvent.objects.get(action="created")])
        self.assertContains(response, "Thema angelegt")
        self.assertNotContains(response, "Thema geändert")
        self.assertContains(response, "action-filter")

    def test_action_filter_combines_with_series_and_topic_filters(self):
        response = self.client.get(reverse("audit_history"), {
            "action": "updated", "series": self.series.pk, "topic": self.topic.pk,
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["selected_action"], "updated")
        self.assertEqual(response.context["selected_series"], str(self.series.pk))
        self.assertEqual(response.context["selected_topic"], str(self.topic.pk))
        self.assertEqual(
            list(response.context["events"]),
            [AuditEvent.objects.get(action="updated")],
        )

    def test_invalid_action_filter_is_ignored(self):
        response = self.client.get(reverse("audit_history"), {"action": "not-a-real-action"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["events"]), 2)
        self.assertEqual(response.context["selected_action"], "")
