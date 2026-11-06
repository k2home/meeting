from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from .models import MeetingSeries, Topic, TopicTransferHistory

User = get_user_model()

class AccountSecurityTests(TestCase):
    def test_unknown_username_does_not_create_account(self):
        response = self.client.post(reverse("login"), {"username": "not-a-user", "password": "wrong"})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="not-a-user").exists())

    def test_valid_password_login(self):
        User.objects.create_user(username="member", password="strong-test-password")
        response = self.client.post(reverse("login"), {"username": "member", "password": "strong-test-password"})
        self.assertRedirects(response, reverse("dashboard"))

class TopicWorkflowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="member", password="strong-test-password")
        self.client.force_login(self.user)
        self.series_a = MeetingSeries.objects.create(name="Reihe A")
        self.series_b = MeetingSeries.objects.create(name="Reihe B")
        self.topic = Topic.objects.create(title="Testthema", series=self.series_a)

    def test_archive_and_reopen_topic(self):
        response = self.client.post(reverse("topic_archive", args=[self.topic.pk]))
        self.assertRedirects(response, reverse("archive"))
        self.topic.refresh_from_db()
        self.assertEqual(self.topic.status, "archived")
        response = self.client.post(reverse("topic_reopen", args=[self.topic.pk]))
        self.assertRedirects(response, reverse("topic_edit", args=[self.topic.pk]))
        self.topic.refresh_from_db()
        self.assertEqual(self.topic.status, "open")

    def test_transfer_records_history(self):
        response = self.client.post(reverse("topic_transfer", args=[self.topic.pk]), {"series": self.series_b.pk, "note": "Zuständigkeit"})
        self.assertRedirects(response, reverse("topic_edit", args=[self.topic.pk]))
        self.topic.refresh_from_db()
        self.assertEqual(self.topic.series, self.series_b)
        history = TopicTransferHistory.objects.get(topic=self.topic)
        self.assertEqual(history.from_series, self.series_a)
        self.assertEqual(history.to_series, self.series_b)
        self.assertEqual(history.transferred_by, self.user)
        self.assertEqual(history.note, "Zuständigkeit")
