from datetime import timedelta
from ipaddress import ip_network
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .forms import AttachmentForm
from .models import AgendaItem, Meeting, MeetingSeries, OrganizationSettings, SeriesAccess, Topic
from .views import _move_future_agenda_items

User = get_user_model()


class RepositoryFollowupHardeningTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="followup-moderator", password="test-password")
        self.series = MeetingSeries.objects.create(name="Folgetest")
        SeriesAccess.objects.create(user=self.user, series=self.series, role=SeriesAccess.ROLE_MODERATOR)
        self.client.force_login(self.user)

    def test_archiving_is_blocked_by_any_unfinalized_meeting_even_if_past(self):
        meeting = Meeting.objects.create(series=self.series, date=timezone.localdate() - timedelta(days=2))
        topic = Topic.objects.create(title="Noch offen", series=self.series)
        AgendaItem.objects.create(meeting=meeting, topic=topic)
        self.client.post(reverse("topic_archive_toggle", args=[topic.pk]))
        topic.refresh_from_db()
        self.assertEqual(topic.status, "open")

    def test_move_merge_preserves_predecessor_and_successor_links(self):
        today = timezone.localdate()
        target_series = MeetingSeries.objects.create(name="Zielreihe")
        source_meeting = Meeting.objects.create(series=self.series, date=today + timedelta(days=2))
        target_meeting = Meeting.objects.create(series=target_series, date=today + timedelta(days=9))
        later_meeting = Meeting.objects.create(series=self.series, date=today + timedelta(days=16))
        topic = Topic.objects.create(title="Verschobener Punkt", series=self.series)
        predecessor_topic = Topic.objects.create(title="Vorgänger", series=self.series)
        child_topic = Topic.objects.create(title="Nachfolger", series=self.series)
        predecessor = AgendaItem.objects.create(meeting=source_meeting, topic=predecessor_topic)
        source = AgendaItem.objects.create(meeting=source_meeting, topic=topic, followup_of=predecessor)
        target = AgendaItem.objects.create(meeting=target_meeting, topic=topic)
        child = AgendaItem.objects.create(meeting=later_meeting, topic=child_topic, followup_of=source)
        _move_future_agenda_items(topic, self.series, target_series)
        target.refresh_from_db()
        child.refresh_from_db()
        self.assertEqual(target.followup_of_id, predecessor.pk)
        self.assertEqual(child.followup_of_id, target.pk)
        self.assertFalse(AgendaItem.objects.filter(pk=source.pk).exists())

    def test_series_reset_rebuilds_links_between_draft_items(self):
        today = timezone.localdate()
        first_date = today + timedelta(days=(self.series.weekday - today.weekday()) % 7)
        if first_date <= today:
            first_date += timedelta(days=7)
        self.series.start_date = first_date
        self.series.weekday = first_date.weekday()
        self.series.end_date = first_date + timedelta(days=14)
        self.series.save(update_fields=["start_date", "weekday", "end_date"])
        first = Meeting.objects.create(series=self.series, date=first_date)
        second = Meeting.objects.create(series=self.series, date=first_date + timedelta(days=7))
        parent_topic = Topic.objects.create(title="Ursprung", series=self.series)
        child_topic = Topic.objects.create(title="Wiedervorlage", series=self.series)
        parent = AgendaItem.objects.create(meeting=first, topic=parent_topic)
        AgendaItem.objects.create(meeting=second, topic=child_topic, followup_of=parent)
        response = self.client.post(reverse("series_reset_meetings", args=[self.series.pk]))
        self.assertEqual(response.status_code, 302)
        restored_parent = AgendaItem.objects.get(topic=parent_topic)
        restored_child = AgendaItem.objects.get(topic=child_topic)
        self.assertEqual(restored_child.followup_of_id, restored_parent.pk)

    def test_upload_limit_is_configurable_and_enforced(self):
        OrganizationSettings.objects.create(attachment_max_size_mb=1)
        oversized = SimpleUploadedFile("large.bin", b"x" * (1024 * 1024 + 1))
        form = AttachmentForm(data={"label": "Zu groß", "network_path": ""}, files={"uploaded_file": oversized})
        self.assertFalse(form.is_valid())
        self.assertIn("uploaded_file", form.errors)

    def test_proxy_cidr_validation_supports_ipv4_and_ipv6(self):
        self.assertEqual(str(ip_network("10.0.0.0/24")), "10.0.0.0/24")
        self.assertEqual(str(ip_network("2001:db8::/64")), "2001:db8::/64")
        script = Path(__file__).resolve().parent.parent / "deploy" / "install-debian.sh"
        content = script.read_text(encoding="utf-8")
        self.assertIn("ipaddress.ip_network", content)
        self.assertIn('s|server_name _;|', content)
