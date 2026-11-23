from datetime import date

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .models import MeetingSeries, SeriesAccess, Topic, TopicAttachment

User = get_user_model()


class UploadedAttachmentMetadataTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="attachment-metadata-user", password="strong-test-password"
        )
        self.series = MeetingSeries.objects.create(name="Anlagen-Reihe")
        SeriesAccess.objects.create(user=self.user, series=self.series)
        self.topic = Topic.objects.create(title="Anlagen-Thema", series=self.series)
        self.upload = SimpleUploadedFile(
            "sitzungsunterlage.pdf", b"PDF-Dateiinhalt"
        )
        TopicAttachment.objects.create(
            topic=self.topic,
            label="Sitzungsunterlage",
            uploaded_file=self.upload,
        )

    def test_topic_page_shows_uploaded_file_size(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("topic_edit", args=[self.topic.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Datei öffnen")
        self.assertContains(response, f'data-file-size="{len(b"PDF-Dateiinhalt")}"')

    def test_user_without_topic_access_cannot_view_attachment_metadata(self):
        outsider = User.objects.create_user(
            username="attachment-outsider", password="strong-test-password"
        )
        self.client.force_login(outsider)

        response = self.client.get(reverse("topic_edit", args=[self.topic.pk]))

        self.assertIn(response.status_code, (403, 404))
