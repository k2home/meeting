from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import AuditEvent, MeetingSeries, SeriesAccess, Topic

User = get_user_model()


class AuditActorFilterTests(TestCase):
    def setUp(self):
        self.moderator = User.objects.create_user(username="actor-filter-moderator", password="test-password")
        self.first_actor = User.objects.create_user(username="first-editor", first_name="Anna", password="test-password")
        self.second_actor = User.objects.create_user(username="second-editor", first_name="Berta", password="test-password")
        self.series = MeetingSeries.objects.create(name="Bearbeiterfilter-Reihe")
        SeriesAccess.objects.create(user=self.moderator, series=self.series, role=SeriesAccess.ROLE_MODERATOR)
        self.topic = Topic.objects.create(title="Bearbeiterfilter-Thema", series=self.series)
        AuditEvent.objects.create(topic=self.topic, series=self.series, actor=self.first_actor, action="updated", summary="Von Anna geändert")
        AuditEvent.objects.create(topic=self.topic, series=self.series, actor=self.second_actor, action="updated", summary="Von Berta geändert")
        self.client.force_login(self.moderator)

    def test_actor_filter_shows_only_events_by_selected_user(self):
        response = self.client.get(reverse("audit_history"), {"actor": self.first_actor.pk})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Von Anna geändert")
        self.assertNotContains(response, "Von Berta geändert")
        self.assertContains(response, "actor-filter")

    def test_unknown_actor_filter_is_ignored(self):
        response = self.client.get(reverse("audit_history"), {"actor": "999999"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["events"].count(), 2)
        self.assertEqual(response.context["selected_actor"], "")
