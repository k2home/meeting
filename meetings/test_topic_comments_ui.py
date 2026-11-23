from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import MeetingSeries, SeriesAccess, Topic, TopicComment

User = get_user_model()


class TopicCommentsPageTests(TestCase):
    def setUp(self):
        self.member = User.objects.create_user(
            username="topic-comment-member", password="strong-test-password",
            first_name="Mira", last_name="Beispiel",
        )
        self.reader = User.objects.create_user(
            username="topic-comment-reader", password="strong-test-password"
        )
        self.series = MeetingSeries.objects.create(name="Kommentar-Reihe")
        SeriesAccess.objects.create(user=self.member, series=self.series)
        SeriesAccess.objects.create(
            user=self.reader, series=self.series, role=SeriesAccess.ROLE_READER
        )
        self.topic = Topic.objects.create(title="Kommentar-Thema", series=self.series)
        TopicComment.objects.create(
            topic=self.topic, author=self.member, body="Bitte Angebot bis Freitag prüfen."
        )

    def test_topic_page_displays_comments_and_comment_form_for_writable_members(self):
        self.client.force_login(self.member)

        response = self.client.get(reverse("topic_edit", args=[self.topic.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Kommentare und nächste Schritte")
        self.assertContains(response, "Bitte Angebot bis Freitag prüfen.")
        self.assertContains(response, "Mira Beispiel")
        self.assertContains(response, reverse("topic_comment_add", args=[self.topic.pk]))
        self.assertContains(response, "Kommentar hinzufügen")

    def test_new_topic_form_still_loads_without_an_existing_topic(self):
        self.client.force_login(self.member)

        response = self.client.get(reverse("topic_new"))

        self.assertEqual(response.status_code, 200)

    def test_reader_can_see_comments_but_cannot_submit_new_ones(self):
        self.client.force_login(self.reader)

        response = self.client.get(reverse("topic_edit", args=[self.topic.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Bitte Angebot bis Freitag prüfen.")
        self.assertNotContains(response, "Kommentar hinzufügen")
        self.assertNotContains(response, reverse("topic_comment_add", args=[self.topic.pk]))
