from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import AgendaItem, Meeting, MeetingSeries, SeriesAccess, Topic


class OpenTopicsWithoutAgendaItemTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="open-topics-user",
            password="strong-test-password",
        )
        self.series = MeetingSeries.objects.create(name="Offene-Punkte-Reihe")
        SeriesAccess.objects.create(
            user=self.user,
            series=self.series,
            role=SeriesAccess.ROLE_PARTICIPANT,
        )
        self.client.force_login(self.user)
        self.today = timezone.localdate()

    def test_active_topic_without_any_agenda_item_is_shown(self):
        topic = Topic.objects.create(
            title="Noch nie auf der Tagesordnung",
            series=self.series,
            status="open",
        )

        response = self.client.get(reverse("open_topics"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, topic.title)
        self.assertContains(response, "Bisher noch nicht auf einer Tagesordnung geführt.")
        self.assertEqual(len(response.context["rows"]), 1)
        self.assertIsNone(response.context["rows"][0]["item"])
        self.assertEqual(response.context["rows"][0]["topic"], topic)

    def test_open_topics_page_renders_series_dropdown_with_current_selection(self):
        other_series = MeetingSeries.objects.create(name="Weitere Reihe")
        SeriesAccess.objects.create(
            user=self.user,
            series=other_series,
            role=SeriesAccess.ROLE_PARTICIPANT,
        )

        response = self.client.get(
            reverse("open_topics"),
            {"series": self.series.pk},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="open-topics-series-filter"')
        self.assertContains(response, f'<option value="{self.series.pk}" selected>')
        self.assertContains(response, other_series.name)
        self.assertContains(response, "Filter zurücksetzen")

    def test_series_filter_shows_only_open_topics_from_selected_series(self):
        selected_topic = Topic.objects.create(
            title="Thema der ausgewählten Reihe",
            series=self.series,
            status="open",
        )
        other_series = MeetingSeries.objects.create(name="Andere Reihe")
        SeriesAccess.objects.create(
            user=self.user,
            series=other_series,
            role=SeriesAccess.ROLE_PARTICIPANT,
        )
        other_topic = Topic.objects.create(
            title="Thema einer anderen Reihe",
            series=other_series,
            status="in_progress",
        )

        response = self.client.get(
            reverse("open_topics"),
            {"series": self.series.pk},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [row["topic"].pk for row in response.context["rows"]],
            [selected_topic.pk],
        )
        self.assertContains(response, selected_topic.title)
        self.assertNotContains(response, other_topic.title)
        self.assertEqual(response.context["selected_series"], self.series.pk)
        self.assertEqual(response.context["selected_series_name"], self.series.name)

    def test_invalid_or_unassigned_series_filter_does_not_show_unfiltered_topics(self):
        topic = Topic.objects.create(
            title="Berechtigtes Thema",
            series=self.series,
            status="open",
        )
        other_series = MeetingSeries.objects.create(name="Nicht zugewiesene Reihe")

        response = self.client.get(
            reverse("open_topics"),
            {"series": other_series.pk},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["rows"], [])
        self.assertNotContains(response, topic.title)

    def test_topic_without_agenda_item_can_be_added_to_future_meeting(self):
        topic = Topic.objects.create(
            title="Erster Tagesordnungspunkt",
            series=self.series,
            status="in_progress",
        )
        meeting = Meeting.objects.create(
            series=self.series,
            date=self.today + timedelta(days=7),
        )

        response = self.client.post(
            reverse("open_topics"),
            {"schedule_topic": topic.pk, "target_meeting": meeting.pk},
        )

        self.assertRedirects(response, reverse("open_topics"))
        item = AgendaItem.objects.get(topic=topic, meeting=meeting)
        self.assertEqual(item.status, "in_progress")
        self.assertEqual(item.working_text, "")
        self.assertFalse(item.carried_forward)
        self.assertIsNone(item.followup_of)


    def test_dashboard_open_topic_counts_match_open_topics_page_criteria(self):
        no_agenda_topic = Topic.objects.create(
            title="Ohne Tagesordnung",
            series=self.series,
            status="open",
        )
        old_meeting = Meeting.objects.create(
            series=self.series,
            date=self.today - timedelta(days=1),
        )
        unfinished_item_topic = Topic.objects.create(
            title="Offener letzter Tagesordnungspunkt",
            series=self.series,
            status="done",
        )
        AgendaItem.objects.create(
            meeting=old_meeting,
            topic=unfinished_item_topic,
            status="in_progress",
        )
        completed_topic = Topic.objects.create(
            title="Abgeschlossen",
            series=self.series,
            status="open",
        )
        AgendaItem.objects.create(
            meeting=old_meeting,
            topic=completed_topic,
            status="done",
        )
        future_topic = Topic.objects.create(
            title="Erst künftig auf der Tagesordnung",
            series=self.series,
            status="open",
        )
        future_meeting = Meeting.objects.create(
            series=self.series,
            date=self.today + timedelta(days=3),
        )
        AgendaItem.objects.create(
            meeting=future_meeting,
            topic=future_topic,
            status="open",
        )
        Meeting.objects.create(
            series=self.series,
            date=self.today + timedelta(days=10),
        )

        open_topics_response = self.client.get(reverse("open_topics"))
        dashboard_response = self.client.get(reverse("dashboard"))

        self.assertEqual(open_topics_response.status_code, 200)
        self.assertEqual(len(open_topics_response.context["rows"]), 2)
        group = next(
            group for group in dashboard_response.context["meeting_groups"]
            if group["series"].pk == self.series.pk
        )
        self.assertEqual(group["open_topic_count"], 2)
        self.assertContains(dashboard_response, '<span class="overdue">2 offene Punkte</span>')
        self.assertContains(dashboard_response, f'href="{reverse("open_topics")}?series={self.series.pk}"')
        self.assertContains(dashboard_response, '<span class="overdue">2</span>')

    def test_dashboard_counts_all_open_topics_in_series_not_only_last_group(self):
        old_meeting = Meeting.objects.create(
            series=self.series,
            date=self.today - timedelta(days=1),
        )
        for index, status in enumerate(("open", "in_progress"), start=1):
            Topic.objects.create(
                title=f"Thema ohne Tagesordnung {index}",
                series=self.series,
                status=status,
            )
        for index, item_status in enumerate(("open", "in_progress"), start=1):
            topic = Topic.objects.create(
                title=f"Thema mit Tagesordnung {index}",
                series=self.series,
                status="done" if index == 1 else "open",
            )
            AgendaItem.objects.create(
                meeting=old_meeting,
                topic=topic,
                status=item_status,
            )
        Meeting.objects.create(
            series=self.series,
            date=self.today + timedelta(days=7),
        )

        open_topics_response = self.client.get(reverse("open_topics"))
        dashboard_response = self.client.get(reverse("dashboard"))

        self.assertEqual(open_topics_response.status_code, 200)
        self.assertEqual(len(open_topics_response.context["rows"]), 4)
        group = next(
            group for group in dashboard_response.context["meeting_groups"]
            if group["series"].pk == self.series.pk
        )
        self.assertEqual(group["open_topic_count"], 4)
        self.assertContains(dashboard_response, '<span class="overdue">4 offene Punkte</span>')


    def test_dashboard_displays_singular_open_topic_label_and_keeps_link(self):
        Topic.objects.create(
            title="Ein offener Punkt",
            series=self.series,
            status="open",
        )
        Meeting.objects.create(
            series=self.series,
            date=self.today + timedelta(days=7),
        )

        response = self.client.get(reverse("dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<span class="overdue">1 offener Punkt</span>')
        self.assertContains(
            response,
            f'href="{reverse("open_topics")}?series={self.series.pk}"',
        )

    def test_completed_or_archived_topics_without_agenda_items_are_not_shown(self):
        Topic.objects.create(
            title="Erledigt",
            series=self.series,
            status="done",
        )
        Topic.objects.create(
            title="Archiviert",
            series=self.series,
            status="archived",
        )

        response = self.client.get(reverse("open_topics"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["rows"], [])
