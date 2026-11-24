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

    def test_network_path_attachment_is_not_shown_as_uploaded_file(self):
        TopicAttachment.objects.create(
            topic=self.topic,
            label="Netzwerkordner",
            network_path=r"\\server\freigabe\unterlage",
        )
        self.client.force_login(self.user)

        response = self.client.get(reverse("topic_edit", args=[self.topic.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, r"\\server\freigabe\unterlage")
        self.assertContains(response, f'data-file-size="{len(b"PDF-Dateiinhalt")}"')
        self.assertNotContains(response, 'data-file-size="0"')

    def test_user_without_topic_access_cannot_view_attachment_metadata(self):
        outsider = User.objects.create_user(
            username="attachment-outsider", password="strong-test-password"
        )
        self.client.force_login(outsider)

        response = self.client.get(reverse("topic_edit", args=[self.topic.pk]))

        self.assertIn(response.status_code, (403, 404))


    def test_attachment_delete_removes_database_record_and_uploaded_file(self):
        attachment = self.topic.attachments.get()
        file_name = attachment.uploaded_file.name
        storage = attachment.uploaded_file.storage
        self.assertTrue(storage.exists(file_name))
        self.client.force_login(self.user)

        response = self.client.post(reverse("attachment_delete", args=[attachment.pk]))

        self.assertRedirects(response, reverse("topic_edit", args=[self.topic.pk]))
        self.assertFalse(TopicAttachment.objects.filter(pk=attachment.pk).exists())
        self.assertFalse(storage.exists(file_name))

    def test_network_path_attachment_can_be_deleted(self):
        attachment = TopicAttachment.objects.create(
            topic=self.topic, label="Netzwerkordner",
            network_path=r"\\server\freigabe\unterlage",
        )
        self.client.force_login(self.user)
        response = self.client.post(reverse("attachment_delete", args=[attachment.pk]))
        self.assertRedirects(response, reverse("topic_edit", args=[self.topic.pk]))
        self.assertFalse(TopicAttachment.objects.filter(pk=attachment.pk).exists())

    def test_user_without_topic_access_cannot_delete_attachment(self):
        attachment = self.topic.attachments.get()
        outsider = User.objects.create_user(
            username="attachment-delete-outsider", password="strong-test-password"
        )
        self.client.force_login(outsider)
        response = self.client.post(reverse("attachment_delete", args=[attachment.pk]))
        self.assertIn(response.status_code, (403, 404))
        self.assertTrue(TopicAttachment.objects.filter(pk=attachment.pk).exists())

    def test_reader_cannot_delete_attachment(self):
        reader = User.objects.create_user(
            username="attachment-delete-reader", password="strong-test-password"
        )
        SeriesAccess.objects.create(user=reader, series=self.series, role=SeriesAccess.ROLE_READER)
        attachment = self.topic.attachments.get()
        self.client.force_login(reader)
        response = self.client.post(reverse("attachment_delete", args=[attachment.pk]))
        self.assertEqual(response.status_code, 403)
        self.assertTrue(TopicAttachment.objects.filter(pk=attachment.pk).exists())

    def test_attachment_delete_rejects_get(self):
        attachment = self.topic.attachments.get()
        self.client.force_login(self.user)
        response = self.client.get(reverse("attachment_delete", args=[attachment.pk]))
        self.assertEqual(response.status_code, 403)
        self.assertTrue(TopicAttachment.objects.filter(pk=attachment.pk).exists())


class DashboardAttachmentDialogTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="dashboard-attachment-user", password="strong-test-password"
        )
        self.series = MeetingSeries.objects.create(name="Dashboard-Anlagen-Reihe")
        SeriesAccess.objects.create(user=self.user, series=self.series)
        self.topic = Topic.objects.create(
            title="Dashboard Anlagen-Thema", series=self.series
        )
        self.client.force_login(self.user)
        self.dashboard_url = reverse("dashboard") + "?q=Dashboard+Anlagen-Thema"

    def test_topic_overview_opens_attachment_dialog_without_leaving_dashboard(self):
        response = self.client.get(self.dashboard_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, f'data-attachments-dialog="dashboard-attachments-dialog-{self.topic.pk}"'
        )
        self.assertContains(
            response, f'id="dashboard-attachments-dialog-{self.topic.pk}"'
        )
        self.assertContains(response, "Anlage hinzufügen")
        self.assertContains(response, "Datei öffnen", count=0)

    def test_upload_from_dashboard_returns_to_same_overview(self):
        response = self.client.post(
            reverse("attachment_add", args=[self.topic.pk]),
            {
                "label": "Übersichtsdatei",
                "uploaded_file": SimpleUploadedFile("uebersicht.pdf", b"PDF-Inhalt"),
                "next": self.dashboard_url,
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], self.dashboard_url)
        self.assertTrue(
            TopicAttachment.objects.filter(topic=self.topic, label="Übersichtsdatei").exists()
        )

    def test_delete_from_dashboard_returns_to_same_overview(self):
        attachment = TopicAttachment.objects.create(
            topic=self.topic, label="Zu löschende Übersichtsdatei",
            network_path=r"\\\\server\\freigabe\\datei",
        )

        response = self.client.post(
            reverse("attachment_delete", args=[attachment.pk]),
            {"next": self.dashboard_url},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], self.dashboard_url)
        self.assertFalse(TopicAttachment.objects.filter(pk=attachment.pk).exists())

    def test_reader_can_view_but_not_edit_dashboard_attachments(self):
        reader = User.objects.create_user(
            username="dashboard-attachment-reader", password="strong-test-password"
        )
        SeriesAccess.objects.create(
            user=reader, series=self.series, role=SeriesAccess.ROLE_READER
        )
        TopicAttachment.objects.create(
            topic=self.topic, label="Nur ansehen", network_path="https://example.org/datei"
        )
        self.client.force_login(reader)

        response = self.client.get(self.dashboard_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Nur ansehen")
        self.assertNotContains(response, "Anlage löschen")
        self.assertNotContains(response, "Anlage hinzufügen")
