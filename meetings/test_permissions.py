from datetime import date

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from .models import Meeting, MeetingSeries, SeriesAccess, Topic

User = get_user_model()


class SeriesRolePermissionTests(TestCase):
    def setUp(self):
        self.user_group, _ = Group.objects.get_or_create(name="Nutzer*in")
        self.moderator_group, _ = Group.objects.get_or_create(name="Moderator*in")
        self.user = User.objects.create_user(username="assigned-user", password="test-password")
        self.user.groups.add(self.user_group)
        self.moderator = User.objects.create_user(username="assigned-moderator", password="test-password")
        self.moderator.groups.add(self.moderator_group)
        self.series_a = MeetingSeries.objects.create(name="Zugewiesene Reihe")
        self.series_b = MeetingSeries.objects.create(name="Nicht zugewiesene Reihe")
        SeriesAccess.objects.create(user=self.user, series=self.series_a)
        SeriesAccess.objects.create(user=self.moderator, series=self.series_a)
        self.meeting = Meeting.objects.create(series=self.series_a, date=date(2026, 12, 1))
        self.other_meeting = Meeting.objects.create(series=self.series_b, date=date(2026, 12, 2))
        self.topic = Topic.objects.create(title="Zugewiesenes Thema", series=self.series_a)
        self.other_topic = Topic.objects.create(title="Fremdes Thema", series=self.series_b)


    def test_reader_can_read_assigned_content_but_cannot_change_it_or_be_a_participant(self):
        from django.contrib.auth.models import Group
        reader_group, _ = Group.objects.get_or_create(name="Leser*in")
        reader = User.objects.create_user(username="series-reader", password="test-password")
        reader.groups.add(reader_group)
        SeriesAccess.objects.create(user=reader, series=self.series_a)

        self.client.force_login(reader)
        meeting_response = self.client.get(reverse("meeting", args=[self.meeting.pk]))
        self.assertEqual(meeting_response.status_code, 200)
        self.assertContains(meeting_response, self.topic.title)
        self.meeting.refresh_from_db()
        self.assertFalse(self.meeting.participants.filter(pk=reader.pk).exists())

        topic_response = self.client.get(reverse("topic_edit", args=[self.topic.pk]))
        self.assertEqual(topic_response.status_code, 200)
        self.assertContains(topic_response, 'disabled')

        denied_edit = self.client.post(reverse("topic_edit", args=[self.topic.pk]), {
            "title": "Manipuliert", "description": "", "status": "open",
            "series": self.series_a.pk,
        })
        self.assertEqual(denied_edit.status_code, 403)
        self.topic.refresh_from_db()
        self.assertEqual(self.topic.title, "Zugewiesenes Thema")

        denied_comment = self.client.post(reverse("topic_comment_add", args=[self.topic.pk]), {"body": "Nicht erlaubt"})
        self.assertEqual(denied_comment.status_code, 403)
        denied_finalize = self.client.post(reverse("finalize", args=[self.meeting.pk]))
        self.assertEqual(denied_finalize.status_code, 403)
        self.meeting.refresh_from_db()
        self.assertIsNone(self.meeting.finalized_at)

        self.assertEqual(self.client.get(reverse("topic_edit", args=[self.other_topic.pk])).status_code, 404)
        self.assertEqual(self.client.get(reverse("topic_new")).status_code, 403)
        from .models import TopicAttachment
        self.assertEqual(self.client.get(reverse("attachment_add", args=[self.topic.pk])).status_code, 403)

    def test_user_cannot_access_unassigned_series_content(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(reverse("meeting", args=[self.other_meeting.pk])).status_code, 404)
        self.assertEqual(self.client.get(reverse("topic_edit", args=[self.other_topic.pk])).status_code, 404)

    def test_user_can_finalize_assigned_meeting(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("finalize", args=[self.meeting.pk]))
        self.assertEqual(response.status_code, 302)
        self.meeting.refresh_from_db()
        self.assertIsNotNone(self.meeting.finalized_at)

    def test_only_moderator_can_reopen_completed_meeting(self):
        from django.utils import timezone
        self.meeting.finalized_at = timezone.now()
        self.meeting.save(update_fields=["finalized_at"])

        self.client.force_login(self.user)
        denied = self.client.post(reverse("meeting_reopen", args=[self.meeting.pk]))
        self.assertEqual(denied.status_code, 302)
        self.meeting.refresh_from_db()
        self.assertIsNotNone(self.meeting.finalized_at)

        self.client.force_login(self.moderator)
        allowed = self.client.post(reverse("meeting_reopen", args=[self.meeting.pk]))
        self.assertEqual(allowed.status_code, 302)
        self.meeting.refresh_from_db()
        self.assertIsNone(self.meeting.finalized_at)

    def test_moderator_can_manage_assigned_series_but_user_cannot(self):
        self.client.force_login(self.user)
        denied = self.client.get(reverse("series_admin"))
        self.assertEqual(denied.status_code, 302)

        self.client.force_login(self.moderator)
        allowed = self.client.get(reverse("series_admin"))
        self.assertEqual(allowed.status_code, 200)
        self.assertContains(allowed, self.series_a.name)
        self.assertNotContains(allowed, self.series_b.name)

    def test_moderator_cannot_edit_unassigned_series(self):
        self.client.force_login(self.moderator)
        response = self.client.get(reverse("series_edit", args=[self.series_b.pk]))
        self.assertEqual(response.status_code, 404)
