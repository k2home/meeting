from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import MeetingSeries, SeriesAccess, Topic, TopicAttachment

User = get_user_model()


class TopicAttachmentSearchTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="topic-attachment-search", password="strong-test-password"
        )
        self.series = MeetingSeries.objects.create(name="Anlagen-Suche")
        SeriesAccess.objects.create(user=self.user, series=self.series)
        self.topic = Topic.objects.create(title="Anlagen-Thema", series=self.series)
        TopicAttachment.objects.create(
            topic=self.topic, label="Sitzungsunterlage",
            network_path="https://example.test/unterlage",
        )
        TopicAttachment.objects.create(
            topic=self.topic, label="Beschlussvorlage",
            network_path="\\\\fileserver\\gremium\\beschluss.pdf",
        )

    def test_topic_page_exposes_accessible_local_attachment_search(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("topic_edit", args=[self.topic.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="topic-attachment-search"')
        self.assertContains(response, 'aria-controls="topic-attachment-list"')
        self.assertContains(response, 'id="topic-attachment-search-status"')
        self.assertContains(response, "Sitzungsunterlage")
        self.assertContains(response, "Beschlussvorlage")
