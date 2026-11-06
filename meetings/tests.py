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


class TopicTaskManagementTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="owner", password="strong-test-password")
        self.member = User.objects.create_user(username="member", password="strong-test-password")
        self.series = MeetingSeries.objects.create(name="Aufgaben-Reihe")
        self.topic = Topic.objects.create(title="Aufgabe", series=self.series)

    def test_topic_can_be_assigned_and_assignment_is_audited(self):
        self.client.force_login(self.member)
        response = self.client.post(reverse("topic_edit", args=[self.topic.pk]), {
            "title": self.topic.title,
            "description": self.topic.description,
            "due_date": "",
            "status": "open",
            "series": self.series.pk,
            "assigned_to": self.owner.pk,
        })
        self.assertRedirects(response, reverse("topic_edit", args=[self.topic.pk]))
        self.topic.refresh_from_db()
        self.assertEqual(self.topic.assigned_to, self.owner)
        from .models import AuditEvent
        event = AuditEvent.objects.get(topic=self.topic, action="updated")
        self.assertEqual(event.changes["Verantwortlich"]["vorher"], None)
        self.assertEqual(event.changes["Verantwortlich"]["nachher"], "owner")

    def test_user_can_add_comment_and_comment_is_audited(self):
        self.client.force_login(self.member)
        response = self.client.post(reverse("topic_comment_add", args=[self.topic.pk]), {
            "body": "Rückmeldung: Angebot wird bis Freitag eingeholt."
        })
        self.assertRedirects(response, reverse("topic_edit", args=[self.topic.pk]))
        from .models import AuditEvent, TopicComment
        comment = TopicComment.objects.get(topic=self.topic)
        self.assertEqual(comment.author, self.member)
        self.assertEqual(comment.body, "Rückmeldung: Angebot wird bis Freitag eingeholt.")
        self.assertTrue(AuditEvent.objects.filter(
            topic=self.topic, actor=self.member, action="comment_added"
        ).exists())

    def test_comment_endpoint_requires_login(self):
        response = self.client.post(reverse("topic_comment_add", args=[self.topic.pk]), {"body": "Test"})
        self.assertEqual(response.status_code, 302)


class MyTasksViewTests(TestCase):
    def setUp(self):
        from datetime import timedelta
        from django.utils import timezone

        self.user = User.objects.create_user(username="task-owner", password="strong-test-password")
        self.other_user = User.objects.create_user(username="other-owner", password="strong-test-password")
        self.series = MeetingSeries.objects.create(name="Meine-Aufgaben-Reihe")
        today = timezone.localdate()
        self.overdue = Topic.objects.create(
            title="Überfällige Aufgabe", series=self.series, assigned_to=self.user,
            due_date=today - timedelta(days=2),
        )
        self.due_today = Topic.objects.create(
            title="Heute fällig", series=self.series, assigned_to=self.user, due_date=today,
        )
        self.no_due_date = Topic.objects.create(
            title="Ohne Fälligkeit", series=self.series, assigned_to=self.user,
        )
        Topic.objects.create(title="Aufgabe anderer Person", series=self.series, assigned_to=self.other_user)
        Topic.objects.create(title="Nicht zugewiesen", series=self.series)
        Topic.objects.create(title="Erledigt", series=self.series, assigned_to=self.user, status="done")
        Topic.objects.create(title="Archiviert", series=self.series, assigned_to=self.user, status="archived")

    def test_my_tasks_shows_only_my_open_topics_and_overdue_summary(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("my_tasks"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context["topics"]), [self.overdue, self.due_today, self.no_due_date])
        self.assertEqual(response.context["overdue_count"], 1)
        self.assertEqual(response.context["due_today_count"], 1)
        self.assertEqual(response.context["without_due_date_count"], 1)
        self.assertContains(response, "Überfällig")
        self.assertContains(response, "Heute fällig")
        self.assertNotContains(response, "Aufgabe anderer Person")
        self.assertNotContains(response, "Nicht zugewiesen")
        self.assertNotContains(response, "Erledigt")
        self.assertNotContains(response, "Archiviert")

    def test_my_tasks_requires_login(self):
        response = self.client.get(reverse("my_tasks"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)
