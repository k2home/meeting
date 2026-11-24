from io import BytesIO
import shutil
import tempfile
import zipfile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import MeetingSeries, SeriesAccess, Topic, TopicAttachment
from .topic_attachment_archive import _archive_filename

User = get_user_model()


class TopicAttachmentZipDownloadTests(TestCase):
    def setUp(self):
        self.media_root = tempfile.mkdtemp(prefix="meeting-test-media-")
        self.settings_override = override_settings(MEDIA_ROOT=self.media_root)
        self.settings_override.enable()
        self.addCleanup(self.settings_override.disable)
        self.addCleanup(shutil.rmtree, self.media_root, True)
        self.user = User.objects.create_user(
            username="topic-zip-user", password="strong-test-password"
        )
        self.series = MeetingSeries.objects.create(name="ZIP-Reihe")
        SeriesAccess.objects.create(user=self.user, series=self.series)
        self.topic = Topic.objects.create(title="ZIP-Testthema", series=self.series)
        TopicAttachment.objects.create(
            topic=self.topic, label="Erste Datei",
            uploaded_file=SimpleUploadedFile("erste.txt", b"Erster Inhalt"),
        )
        TopicAttachment.objects.create(
            topic=self.topic, label="Zweite Datei",
            uploaded_file=SimpleUploadedFile("zweite.txt", b"Zweiter Inhalt"),
        )
        TopicAttachment.objects.create(
            topic=self.topic, label="Nur ein Link",
            network_path="https://example.test/datei",
        )

    def test_download_contains_all_uploaded_files_but_not_network_links(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("topic_attachments_zip", args=[self.topic.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/zip")
        with zipfile.ZipFile(BytesIO(response.content)) as archive:
            self.assertEqual(set(archive.namelist()), {"erste.txt", "zweite.txt"})
            self.assertEqual(archive.read("erste.txt"), b"Erster Inhalt")
            self.assertEqual(archive.read("zweite.txt"), b"Zweiter Inhalt")

    def test_archive_names_are_reduced_to_basenames_and_made_unique(self):
        used_names = set()

        self.assertEqual(
            _archive_filename("../../bericht.txt", used_names, 1),
            "bericht.txt",
        )
        self.assertEqual(
            _archive_filename(r"C:\\temp\\bericht.txt", used_names, 2),
            "bericht (2).txt",
        )

    def test_user_without_topic_access_cannot_download_zip(self):
        outsider = User.objects.create_user(
            username="topic-zip-outsider", password="strong-test-password"
        )
        self.client.force_login(outsider)

        response = self.client.get(
            reverse("topic_attachments_zip", args=[self.topic.pk])
        )

        self.assertEqual(response.status_code, 404)

    def test_anonymous_user_is_redirected_to_login(self):
        response = self.client.get(
            reverse("topic_attachments_zip", args=[self.topic.pk])
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)
