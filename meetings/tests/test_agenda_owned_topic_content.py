from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from meetings.models import AgendaItem, Meeting, MeetingSeries, SeriesAccess, Topic, TopicSnapshot

User = get_user_model()


class AgendaOwnedTopicContentTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="agenda-editor", password="strong-test-password")
        self.series = MeetingSeries.objects.create(name="Agenda-Reihe")
        SeriesAccess.objects.create(user=self.user, series=self.series)
        self.client.force_login(self.user)
        self.topic = Topic.objects.create(
            title="Strategisches Thema",
            description="Bisherige Beschreibung muss erhalten bleiben",
            series=self.series,
        )

    def test_topic_view_shows_meeting_texts_and_legacy_description_without_topic_status(self):
        first = Meeting.objects.create(series=self.series, date="2026-10-06", finalized_at="2026-10-06T10:00:00Z")
        second = Meeting.objects.create(series=self.series, date="2026-12-01")
        AgendaItem.objects.create(meeting=first, topic=self.topic, working_text="Alter Tagesordnungstext")
        AgendaItem.objects.create(meeting=second, topic=self.topic, working_text="Aktueller Tagesordnungstext")
        TopicSnapshot.objects.create(
            meeting=first, topic_title=self.topic.title, text="Gesicherter alter Protokolltext",
            status="open", topic_id=self.topic.pk,
        )

        response = self.client.get(reverse("topic_edit", args=[self.topic.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Gesicherter alter Protokolltext")
        self.assertContains(response, "Aktueller Tagesordnungstext")
        self.assertContains(response, "Bisherige Beschreibung muss erhalten bleiben")
        self.assertNotContains(response, "Abschlussvermerk")
        self.assertNotContains(response, "Themenstatus")
        self.assertNotContains(response, "Beschreibung und aktueller Stand")

    def test_topic_view_can_edit_text_for_a_specific_unfinalized_meeting(self):
        meeting = Meeting.objects.create(series=self.series, date="2026-12-08")
        item = AgendaItem.objects.create(meeting=meeting, topic=self.topic, working_text="Vorheriger Text")

        response = self.client.post(
            reverse("topic_agenda_edit", args=[self.topic.pk, item.pk]),
            {"working_text": "Überarbeiteter Text", "assigned_to": str(self.user.pk)},
        )

        self.assertRedirects(response, reverse("topic_edit", args=[self.topic.pk]))
        item.refresh_from_db()
        self.topic.refresh_from_db()
        self.assertEqual(item.working_text, "Überarbeiteter Text")
        self.assertEqual(item.assigned_to, self.user)
        self.assertEqual(self.topic.description, "Bisherige Beschreibung muss erhalten bleiben")

    def test_finalized_meeting_text_is_read_only(self):
        meeting = Meeting.objects.create(
            series=self.series, date="2026-11-10", finalized_at="2026-11-10T10:00:00Z"
        )
        item = AgendaItem.objects.create(meeting=meeting, topic=self.topic, working_text="Gesicherter Text")

        response = self.client.post(
            reverse("topic_agenda_edit", args=[self.topic.pk, item.pk]),
            {"working_text": "Darf nicht geändert werden", "assigned_to": ""},
        )

        self.assertEqual(response.status_code, 403)
        item.refresh_from_db()
        self.assertEqual(item.working_text, "Gesicherter Text")

    def test_new_topic_form_contains_no_description_or_status_field(self):
        response = self.client.get(reverse("topic_new"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Erster Besprechungstermin")
        self.assertNotContains(response, "Aktueller Stand")
        self.assertNotContains(response, "Status")
