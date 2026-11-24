from datetime import date

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .models import AgendaItem, Meeting, MeetingSeries, SeriesAccess, Topic, TopicAttachment

User = get_user_model()


class AgendaItemAttachmentTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="agenda-attachment-user", password="strong-test-password"
        )
        self.series = MeetingSeries.objects.create(name="Agenda-Anlagen-Reihe")
        SeriesAccess.objects.create(user=self.user, series=self.series)
        self.meeting = Meeting.objects.create(series=self.series, date=date(2026, 12, 1))
        self.topic = Topic.objects.create(title="Anlagen zum Tagesordnungspunkt", series=self.series)
        self.item = AgendaItem.objects.create(
            meeting=self.meeting, topic=self.topic, position=0
        )
        self.client.force_login(self.user)

    def test_agenda_has_attachments_button_between_shift_and_history(self):
        response = self.client.get(reverse("meeting", args=[self.meeting.pk]))

        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        shift = content.index(">Schieben</button>")
        attachments = content.index(">Anlagen", shift)
        history = content.index(">Historie</button>", attachments)
        self.assertLess(shift, attachments)
        self.assertLess(attachments, history)
        self.assertContains(response, f'id="agenda-attachments-dialog-{self.item.pk}"')
        self.assertContains(response, "Anlage hinzufügen")

    def test_agenda_attachment_upload_is_assigned_to_the_item_topic(self):
        response = self.client.post(
            reverse("agenda_attachment_add", args=[self.meeting.pk, self.item.pk]),
            {
                "label": "Beschlussvorlage",
                "uploaded_file": SimpleUploadedFile("vorlage.pdf", b"PDF-Inhalt"),
            },
        )

        self.assertEqual(response.status_code, 302)
        attachment = TopicAttachment.objects.get(topic=self.topic)
        self.assertEqual(attachment.label, "Beschlussvorlage")
        self.assertTrue(attachment.uploaded_file.storage.exists(attachment.uploaded_file.name))
        self.assertIn(f"?attachments={self.item.pk}#agenda-item-{self.item.pk}", response["Location"])

    def test_agenda_attachment_upload_rejects_disallowed_file_extension(self):
        response = self.client.post(
            reverse("agenda_attachment_add", args=[self.meeting.pk, self.item.pk]),
            {
                "label": "Ausführbare Datei",
                "uploaded_file": SimpleUploadedFile("programm.exe", b"not-an-executable"),
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(TopicAttachment.objects.filter(topic=self.topic).exists())
        self.assertContains(response, "Datei-Upload")

    def test_agenda_attachment_upload_rejects_reader(self):
        reader = User.objects.create_user(
            username="agenda-attachment-reader", password="strong-test-password"
        )
        SeriesAccess.objects.create(
            user=reader, series=self.series, role=SeriesAccess.ROLE_READER
        )
        self.client.force_login(reader)

        response = self.client.post(
            reverse("agenda_attachment_add", args=[self.meeting.pk, self.item.pk]),
            {"label": "Nicht erlaubt", "network_path": r"\\server\freigabe\datei"},
        )

        self.assertEqual(response.status_code, 403)
        self.assertFalse(TopicAttachment.objects.filter(topic=self.topic).exists())

    def test_agenda_attachment_dialog_lists_existing_network_attachment(self):
        TopicAttachment.objects.create(
            topic=self.topic, label="Netzwerkunterlage",
            network_path=r"\\server\freigabe\unterlage",
        )

        response = self.client.get(reverse("meeting", args=[self.meeting.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Netzwerkunterlage")
        self.assertContains(response, r"\\server\freigabe\unterlage")
        self.assertContains(response, "Anlage löschen")
