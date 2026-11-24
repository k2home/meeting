from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import AuditEvent, Meeting, MeetingSeries, SeriesAccess, Topic

User = get_user_model()


class TopicPriorityTests(TestCase):
    def setUp(self):
        self.member = User.objects.create_user(
            username="topic-priority-member", password="strong-test-password"
        )
        self.reader = User.objects.create_user(
            username="topic-priority-reader", password="strong-test-password"
        )
        self.series = MeetingSeries.objects.create(name="Prioritäts-Reihe")
        SeriesAccess.objects.create(user=self.member, series=self.series, role=SeriesAccess.ROLE_PARTICIPANT)
        SeriesAccess.objects.create(
            user=self.reader, series=self.series, role=SeriesAccess.ROLE_READER
        )
        self.topic = Topic.objects.create(title="Prioritätsthema", series=self.series)

    def test_existing_topics_default_to_normal_priority(self):
        self.assertEqual(self.topic.priority, "normal")
        self.assertEqual(self.topic.get_priority_display(), "Normal")

    def test_member_can_change_priority_and_change_is_audited(self):
        self.client.force_login(self.member)

        response = self.client.post(reverse("topic_edit", args=[self.topic.pk]), {
            "title": self.topic.title,
            "priority": "urgent",
        })

        self.assertEqual(response.status_code, 302)
        self.topic.refresh_from_db()
        self.assertEqual(self.topic.priority, "urgent")
        event = AuditEvent.objects.get(topic=self.topic, action="updated")
        self.assertEqual(event.changes["Priorität"]["nachher"], "Dringend")

    def test_member_can_set_priority_when_creating_topic(self):
        meeting = Meeting.objects.create(
            series=self.series, date=timezone.localdate() + timedelta(days=2),
        )
        self.client.force_login(self.member)

        response = self.client.post(reverse("topic_new"), {
            "title": "Neues dringendes Thema",
            "series": self.series.pk,
            "priority": "urgent",
            "meeting": meeting.pk,
        })

        self.assertEqual(response.status_code, 302)
        topic = Topic.objects.get(title="Neues dringendes Thema")
        self.assertEqual(topic.priority, "urgent")

    def test_reader_sees_priority_but_cannot_change_it(self):
        self.client.force_login(self.reader)

        response = self.client.get(reverse("topic_edit", args=[self.topic.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Priorität")
        self.assertContains(response, "disabled")
        self.assertNotContains(response, "Änderungen speichern")
