from django.contrib.auth import get_user_model
from django.apps import apps
from django.db import connection
from types import SimpleNamespace
from importlib import import_module
from django.test import TestCase
from django.urls import reverse

from .models import AgendaItem, AuditEvent, Meeting, MeetingSeries, SeriesAccess, Topic, TopicSnapshot

User = get_user_model()


class AgendaOwnedTopicContentTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="agenda-editor", password="strong-test-password")
        self.series = MeetingSeries.objects.create(name="Agenda-Reihe")
        SeriesAccess.objects.create(user=self.user, series=self.series)
        self.client.force_login(self.user)
        self.topic = Topic.objects.create(
            title="Strategisches Thema",
            series=self.series,
        )

    def test_topic_view_shows_meeting_texts_without_legacy_topic_description_or_status(self):
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
        self.assertNotContains(response, "Bisherige Themenbeschreibung")
        self.assertNotContains(response, "Abschlussvermerk")
        self.assertNotContains(response, "Themenstatus")
        self.assertNotContains(response, "Beschreibung und aktueller Stand")


    def test_topic_detail_columns_start_at_same_top_edge(self):
        response = self.client.get(reverse("topic_edit", args=[self.topic.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<div class="topic-main">')
        self.assertNotContains(response, '<main class="topic-main">')
        self.assertContains(response, '.topic-layout>.topic-main{margin:0;padding:0;width:auto}')

    def test_sidebar_navigation_groups_have_requested_order_and_separation(self):
        from pathlib import Path

        template = Path("templates/meetings/base.html").read_text()
        overview = template.index('class="nav-overview"')
        tasks = template.index('class="nav-tasks"')
        open_topics = template.index('class="nav-open-topics"')
        archive = template.index('class="nav-archive"')
        history = template.index('class="nav-history"')
        series = template.index('class="nav-series"')
        management = template.index('class="sidebar-footer"')
        self.assertLess(overview, tasks)
        self.assertLess(tasks, open_topics)
        self.assertLess(open_topics, archive)
        self.assertLess(archive, history)
        self.assertLess(history, series)
        self.assertLess(series, management)
        self.assertIn('class="nav-links nav-links-secondary"', template)

    def test_topic_detail_omits_redundant_header_and_title_label(self):
        response = self.client.get(reverse("topic_edit", args=[self.topic.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, f"Thema #{self.topic.pk}")
        self.assertNotContains(response, '<label for="id_title">Titel</label>')
        self.assertContains(response, "<h2>Thema</h2>")
        self.assertContains(response, '<label for="id_title">Thementitel</label>')
        self.assertContains(response, self.topic.title)

    def test_audit_cleanup_removes_topic_description_values(self):
        event = AuditEvent.objects.create(
            topic=self.topic,
            action="updated",
            summary="Thema geändert",
            changes={
                "Beschreibung": {"vorher": "Zu löschender Alttext", "nachher": "Neuer Alttext"},
                "Status": {"vorher": "Offen", "nachher": "In Arbeit"},
                "nested": [{"Aktueller Stand": "Auch löschen", "keep": "Behalten"}],
            },
        )
        orphaned_event = AuditEvent.objects.create(
            topic=None, action="updated", summary="Thema „Gelöscht“ geändert",
            changes={"Beschreibung": {"vorher": "Orphan-Alttext"}},
        )
        migration = import_module("meetings.migrations.0020_remove_topic_description")
        migration.remove_topic_description_from_audit(
            apps, SimpleNamespace(connection=connection)
        )
        event.refresh_from_db()
        self.assertNotIn("Beschreibung", event.changes)
        self.assertNotIn("Aktueller Stand", event.changes["nested"][0])
        self.assertEqual(event.changes["Status"]["nachher"], "In Arbeit")
        self.assertEqual(event.changes["nested"][0]["keep"], "Behalten")
        orphaned_event.refresh_from_db()
        self.assertNotIn("Beschreibung", orphaned_event.changes)

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
        self.assertNotIn("description", {field.name for field in Topic._meta.get_fields()})

    def test_dashboard_search_finds_agenda_text(self):
        meeting = Meeting.objects.create(series=self.series, date="2026-12-15")
        AgendaItem.objects.create(
            meeting=meeting, topic=self.topic,
            working_text="Einmaliger historischer Suchbegriff", assigned_to=self.user,
        )
        response = self.client.get(reverse("dashboard"), {"q": "historischer Suchbegriff", "due": ""})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.topic.title)

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
        self.assertNotContains(response, "Beschreibung / Arbeitsauftrag")
        self.assertNotContains(response, "Status")
