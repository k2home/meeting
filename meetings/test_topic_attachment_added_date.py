from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import MeetingSeries, SeriesAccess, Topic, TopicAttachment

User = get_user_model()


class TopicAttachmentAddedDateTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="attachment-date-user", password="strong-test-password"
        )
        self.series = MeetingSeries.objects.create(name="Anlagen-Datum")
        SeriesAccess.objects.create(user=self.user, series=self.series)
        self.topic = Topic.objects.create(title="Anlagen-Datumsthema", series=self.series)
        self.attachment = TopicAttachment.objects.create(
            topic=self.topic, label="Datierte Unterlage",
            network_path="https://example.test/dated-file",
        )

    def test_topic_page_displays_attachment_added_timestamp(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("topic_edit", args=[self.topic.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Datierte Unterlage")
        self.assertContains(response, "Hinzugefügt am")
        self.assertContains(
            response,
            self.attachment.added_at.strftime("%d.%m.%Y"),
        )
