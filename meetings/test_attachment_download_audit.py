from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import TestCase
from django.urls import reverse

from .models import AuditEvent, MeetingSeries, SeriesAccess, Topic, TopicAttachment

User = get_user_model()


class AttachmentDownloadAuditTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="attachment-auditor", password="strong-test-password"
        )
        self.series = MeetingSeries.objects.create(name="Download-Audit-Reihe")
        SeriesAccess.objects.create(user=self.user, series=self.series, role=SeriesAccess.ROLE_PARTICIPANT)
        self.topic = Topic.objects.create(title="Download-Audit-Thema", series=self.series)
        self.attachment = TopicAttachment.objects.create(
            topic=self.topic, label="Sitzungsunterlage"
        )

    @patch("meetings.secure_files.serve_topic_upload", return_value=HttpResponse("file"))
    def test_successful_download_creates_audit_event(self, serve_file):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("attachment_download", args=[self.attachment.pk])
        )

        self.assertEqual(response.status_code, 200)
        serve_file.assert_called_once()
        event = AuditEvent.objects.get(
            topic=self.topic, action="attachment_downloaded"
        )
        self.assertEqual(event.actor, self.user)
        self.assertIn("Sitzungsunterlage", event.summary)

    @patch("meetings.secure_files.serve_topic_upload", return_value=HttpResponse("not found", status=404))
    def test_failed_download_does_not_create_audit_event(self, serve_file):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("attachment_download", args=[self.attachment.pk])
        )

        self.assertEqual(response.status_code, 404)
        self.assertFalse(
            AuditEvent.objects.filter(action="attachment_downloaded").exists()
        )

    def test_user_without_topic_access_cannot_download_or_create_audit_event(self):
        outsider = User.objects.create_user(
            username="attachment-outsider-audit", password="strong-test-password"
        )
        self.client.force_login(outsider)

        response = self.client.get(
            reverse("attachment_download", args=[self.attachment.pk])
        )

        self.assertEqual(response.status_code, 404)
        self.assertFalse(
            AuditEvent.objects.filter(action="attachment_downloaded").exists()
        )

    def test_anonymous_user_is_redirected_to_login(self):
        response = self.client.get(
            reverse("attachment_download", args=[self.attachment.pk])
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)
