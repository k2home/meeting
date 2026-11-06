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


class AuditHistoryTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="auditor", password="strong-test-password")
        self.series = MeetingSeries.objects.create(name="Audit-Reihe")
        self.topic = Topic.objects.create(title="Audit-Thema", series=self.series)

    def test_topic_edit_records_field_changes_and_actor(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("topic_edit", args=[self.topic.pk]), {
            "title": "Neuer Titel",
            "description": "Neue Beschreibung",
            "due_date": "2026-12-01",
            "status": "open",
            "series": self.series.pk,
        })
        self.assertRedirects(response, reverse("topic_edit", args=[self.topic.pk]))
        from .models import AuditEvent
        event = AuditEvent.objects.get(topic=self.topic, action="updated")
        self.assertEqual(event.actor, self.user)
        self.assertEqual(event.changes["Titel"]["vorher"], "Audit-Thema")
        self.assertEqual(event.changes["Titel"]["nachher"], "Neuer Titel")
        self.assertEqual(event.changes["Beschreibung"]["nachher"], "Neue Beschreibung")

    def test_archive_and_reopen_are_logged(self):
        self.client.force_login(self.user)
        self.client.post(reverse("topic_archive", args=[self.topic.pk]))
        self.client.post(reverse("topic_reopen", args=[self.topic.pk]))
        from .models import AuditEvent
        actions = list(AuditEvent.objects.filter(topic=self.topic).order_by("created_at").values_list("action", flat=True))
        self.assertEqual(actions, ["archived", "reopened"])

    def test_history_page_requires_login_and_displays_entries(self):
        from .models import AuditEvent
        AuditEvent.objects.create(topic=self.topic, actor=self.user, action="created", summary="Testeintrag")
        response = self.client.get(reverse("audit_history"))
        self.assertEqual(response.status_code, 302)
        self.client.force_login(self.user)
        response = self.client.get(reverse("audit_history"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Testeintrag")
