from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import AuditEvent, MeetingSeries, SeriesAccess, Topic

User = get_user_model()


class TopicPrimaryAssigneeTests(TestCase):
    def setUp(self):
        self.editor = User.objects.create_user(
            username="topic-owner-editor", password="strong-test-password"
        )
        self.assignee = User.objects.create_user(
            username="topic-primary-assignee", first_name="Alex", last_name="Beispiel",
            password="strong-test-password",
        )
        self.series = MeetingSeries.objects.create(name="Hauptzuständigkeit-Reihe")
        SeriesAccess.objects.create(user=self.editor, series=self.series)
        self.topic = Topic.objects.create(
            title="Thema mit Hauptzuständigkeit", series=self.series
        )
        self.client.force_login(self.editor)
        self.url = reverse("topic_edit", args=[self.topic.pk])

    def test_topic_primary_assignee_can_be_set_and_is_audited(self):
        response = self.client.post(
            self.url,
            {"title": self.topic.title, "assigned_to": str(self.assignee.pk)},
        )

        self.assertRedirects(response, self.url)
        self.topic.refresh_from_db()
        self.assertEqual(self.topic.assigned_to_id, self.assignee.pk)
        event = AuditEvent.objects.filter(topic=self.topic, action="updated").latest("pk")
        self.assertEqual(
            event.changes["Hauptzuständigkeit"],
            {"vorher": None, "nachher": "Alex Beispiel"},
        )

    def test_topic_primary_assignee_can_be_cleared(self):
        self.topic.assigned_to = self.assignee
        self.topic.save(update_fields=["assigned_to"])
        response = self.client.post(
            self.url, {"title": self.topic.title, "assigned_to": ""}
        )

        self.assertRedirects(response, self.url)
        self.topic.refresh_from_db()
        self.assertIsNone(self.topic.assigned_to_id)

    def test_reader_cannot_change_topic_primary_assignee(self):
        reader = User.objects.create_user(
            username="topic-owner-reader", password="strong-test-password"
        )
        SeriesAccess.objects.create(
            user=reader, series=self.series, role=SeriesAccess.ROLE_READER
        )
        self.client.force_login(reader)

        response = self.client.post(
            self.url,
            {"title": self.topic.title, "assigned_to": str(self.assignee.pk)},
        )

        self.assertEqual(response.status_code, 403)
        self.topic.refresh_from_db()
        self.assertIsNone(self.topic.assigned_to_id)

    def test_topic_page_displays_primary_assignee_control(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Hauptzuständigkeit")
        self.assertContains(response, "Die Hauptzuständigkeit gilt für das gesamte Thema.")
