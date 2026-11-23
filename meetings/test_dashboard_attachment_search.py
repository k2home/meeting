from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import AgendaItem, Meeting, MeetingSeries, SeriesAccess, Topic, TopicAttachment

User = get_user_model()


class DashboardAttachmentSearchTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="attachment-search", password="test-password")
        self.series = MeetingSeries.objects.create(name="Anlagen-Suchreihe")
        SeriesAccess.objects.create(user=self.user, series=self.series, role=SeriesAccess.ROLE_PARTICIPANT)
        self.topic = Topic.objects.create(title="Dokumentation", series=self.series)
        meeting = Meeting.objects.create(series=self.series, date=timezone.localdate() + timedelta(days=3))
        AgendaItem.objects.create(meeting=meeting, topic=self.topic, working_text="Besprechung", assigned_to=self.user)
        TopicAttachment.objects.create(topic=self.topic, label="Brandschutzplan", network_path="\\\\server\\\\planung\\\\plan.pdf")

    def test_dashboard_search_finds_attachment_labels(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("dashboard"), {"q": "Brandschutzplan"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dokumentation")

    def test_attachment_search_keeps_permissions_and_deduplicates_topics(self):
        TopicAttachment.objects.create(
            topic=self.topic, label="Brandschutzplan Kopie", network_path="",
        )
        other_user = User.objects.create_user(username="attachment-search-other", password="test-password")
        private_series = MeetingSeries.objects.create(name="Private Anlagenreihe")
        private_topic = Topic.objects.create(title="Vertrauliches Dokument", series=private_series)
        TopicAttachment.objects.create(topic=private_topic, label="Brandschutzplan", network_path="")

        self.client.force_login(self.user)
        response = self.client.get(reverse("dashboard"), {"q": "Brandschutzplan"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["topics"].count(), 1)
        self.assertContains(response, "Dokumentation")
        self.assertNotContains(response, "Vertrauliches Dokument")

    def test_dashboard_search_finds_attachment_paths(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("dashboard"), {"q": "planung"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dokumentation")
