from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import AgendaItem, Meeting, MeetingSeries, SeriesAccess, Topic, TopicComment

User = get_user_model()


class DashboardCommentSearchTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="comment-search", password="test-password")
        self.series = MeetingSeries.objects.create(name="Suchreihe")
        SeriesAccess.objects.create(user=self.user, series=self.series, role=SeriesAccess.ROLE_PARTICIPANT)
        self.topic = Topic.objects.create(title="Reguläres Thema", series=self.series)
        meeting = Meeting.objects.create(series=self.series, date=timezone.localdate() + timedelta(days=3))
        AgendaItem.objects.create(meeting=meeting, topic=self.topic, working_text="Agenda", assigned_to=self.user)
        TopicComment.objects.create(topic=self.topic, author=self.user, body="Bitte Rückmeldung vom Brandschutz einholen.")
        self.client.force_login(self.user)

    def test_dashboard_search_finds_terms_in_topic_comments_without_duplicates(self):
        TopicComment.objects.create(
            topic=self.topic, author=self.user,
            body="Brandschutz-Unterlagen bitte ebenfalls prüfen.",
        )
        response = self.client.get(reverse("dashboard"), {"q": "Brandschutz"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Reguläres Thema")
        self.assertEqual(response.context["topics"].count(), 1)

    def test_dashboard_comment_search_is_case_insensitive(self):
        for search_term in ("brandschutz", "BRANDSCHUTZ", "BrAnDsChUtZ"):
            with self.subTest(search_term=search_term):
                response = self.client.get(reverse("dashboard"), {"q": search_term})
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, "Reguläres Thema")
                self.assertEqual(response.context["topics"].count(), 1)

    def test_dashboard_comment_search_keeps_series_permissions(self):
        other_user = User.objects.create_user(username="comment-search-other", password="test-password")
        other_series = MeetingSeries.objects.create(name="Private Suchreihe")
        other_topic = Topic.objects.create(title="Vertrauliches Thema", series=other_series)
        TopicComment.objects.create(topic=other_topic, author=other_user, body="Brandschutz")
        response = self.client.get(reverse("dashboard"), {"q": "Brandschutz"})
        self.assertNotContains(response, "Vertrauliches Thema")
    def test_dashboard_search_ignores_all_filters(self):
        response = self.client.get(reverse("dashboard"), {
            "q": "Brandschutz",
            "due": "future",
            "status": "done",
            "series": "999999",
            "assigned_to": "unassigned",
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["topics"].count(), 1)
        self.assertEqual(response.context["selected_status"], "all")
        self.assertEqual(response.context["selected_series"], "")
        self.assertEqual(response.context["selected_assignee"], "")
        self.assertEqual(response.context["selected_due"], "")
        self.assertContains(response, 'name="q" value="Brandschutz"')
        self.assertNotContains(response, 'type="hidden" name="status"')
        self.assertNotContains(response, 'type="hidden" name="due"')

    def test_dashboard_filters_keep_selected_values_without_search(self):
        response = self.client.get(reverse("dashboard"), {
            "due": "future",
            "status": "done",
            "series": str(self.series.pk),
            "assigned_to": "unassigned",
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["selected_due"], "future")
        self.assertEqual(response.context["selected_status"], "done")
        self.assertEqual(response.context["selected_series"], str(self.series.pk))
        self.assertEqual(response.context["selected_assignee"], "unassigned")
        self.assertContains(response, f'href="{reverse("dashboard")}"')
