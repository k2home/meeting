from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from .models import Meeting, MeetingSeries, SeriesAccess, Topic, TopicTransferHistory, AgendaItem

User = get_user_model()

class AccountSecurityTests(TestCase):
    def test_unknown_username_does_not_create_account(self):
        response = self.client.post(reverse("login"), {"username": "not-a-user", "password": "wrong"})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="not-a-user").exists())

    def test_valid_password_login(self):
        User.objects.create_user(username="member", password="strong-test-password")
        response = self.client.post(reverse("login"), {"username": "member", "password": "strong-test-password"})
        self.assertRedirects(response, reverse("dashboard"))

class TopicWorkflowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="member", password="strong-test-password")
        self.client.force_login(self.user)
        self.series_a = MeetingSeries.objects.create(name="Reihe A")
        self.series_b = MeetingSeries.objects.create(name="Reihe B")
        SeriesAccess.objects.create(user=self.user, series=self.series_a)
        SeriesAccess.objects.create(user=self.user, series=self.series_b)
        self.topic = Topic.objects.create(title="Testthema", series=self.series_a)

    def test_archive_and_reopen_topic(self):
        response = self.client.post(reverse("topic_archive", args=[self.topic.pk]))
        self.assertRedirects(response, reverse("archive"))
        self.topic.refresh_from_db()
        self.assertEqual(self.topic.status, "archived")
        response = self.client.post(reverse("topic_reopen", args=[self.topic.pk]))
        self.assertRedirects(response, reverse("topic_edit", args=[self.topic.pk]))
        self.topic.refresh_from_db()
        self.assertEqual(self.topic.status, "open")

    def test_transfer_records_history(self):
        response = self.client.post(reverse("topic_transfer", args=[self.topic.pk]), {"series": self.series_b.pk, "note": "Zuständigkeit"})
        self.assertRedirects(response, reverse("topic_edit", args=[self.topic.pk]))
        self.topic.refresh_from_db()
        self.assertEqual(self.topic.series, self.series_b)
        history = TopicTransferHistory.objects.get(topic=self.topic)
        self.assertEqual(history.from_series, self.series_a)
        self.assertEqual(history.to_series, self.series_b)
        self.assertEqual(history.transferred_by, self.user)
        self.assertEqual(history.note, "Zuständigkeit")


class AuditHistoryTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="auditor", password="strong-test-password")
        self.series = MeetingSeries.objects.create(name="Audit-Reihe")
        SeriesAccess.objects.create(user=self.user, series=self.series)
        self.topic = Topic.objects.create(title="Audit-Thema", series=self.series)

    def test_topic_edit_records_field_changes_and_actor(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("topic_edit", args=[self.topic.pk]), {
            "title": "Neuer Titel",
            "description": "Neue Beschreibung",
            "due_date": "2026-12-01",
            "status": "open",
            "series": self.series.pk,
        })
        self.assertRedirects(response, reverse("topic_edit", args=[self.topic.pk]))
        from .models import AuditEvent
        event = AuditEvent.objects.get(topic=self.topic, action="updated")
        self.assertEqual(event.actor, self.user)
        self.assertEqual(event.changes["Titel"]["vorher"], "Audit-Thema")
        self.assertEqual(event.changes["Titel"]["nachher"], "Neuer Titel")
        self.assertEqual(event.changes["Beschreibung"]["nachher"], "Neue Beschreibung")

    def test_archive_and_reopen_are_logged(self):
        self.client.force_login(self.user)
        self.client.post(reverse("topic_archive", args=[self.topic.pk]))
        self.client.post(reverse("topic_reopen", args=[self.topic.pk]))
        from .models import AuditEvent
        actions = list(AuditEvent.objects.filter(topic=self.topic).order_by("created_at").values_list("action", flat=True))
        self.assertEqual(actions, ["archived", "reopened"])

    def test_history_page_requires_login_and_displays_entries(self):
        from .models import AuditEvent
        AuditEvent.objects.create(topic=self.topic, actor=self.user, action="created", summary="Testeintrag")
        response = self.client.get(reverse("audit_history"))
        self.assertEqual(response.status_code, 302)
        SeriesAccess.objects.filter(user=self.user, series=self.series).update(role=SeriesAccess.ROLE_MODERATOR)
        self.client.force_login(self.user)
        response = self.client.get(reverse("audit_history"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Testeintrag")

    def test_history_can_be_filtered_by_meeting_series(self):
        from .models import AuditEvent
        other_series = MeetingSeries.objects.create(name="Weitere Audit-Reihe")
        SeriesAccess.objects.create(user=self.user, series=other_series, role=SeriesAccess.ROLE_MODERATOR)
        other_topic = Topic.objects.create(title="Anderes Audit-Thema", series=other_series)
        AuditEvent.objects.create(topic=self.topic, actor=self.user, action="created", summary="Eintrag aus Audit-Reihe")
        AuditEvent.objects.create(topic=other_topic, actor=self.user, action="created", summary="Eintrag aus weiterer Reihe")
        SeriesAccess.objects.filter(user=self.user, series=self.series).update(role=SeriesAccess.ROLE_MODERATOR)
        self.client.force_login(self.user)

        response = self.client.get(reverse("audit_history"), {"series": self.series.pk})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Eintrag aus Audit-Reihe")
        self.assertNotContains(response, "Eintrag aus weiterer Reihe")
        self.assertContains(response, "Weitere Audit-Reihe")

    def test_history_only_shows_series_where_user_is_moderator(self):
        from .models import AuditEvent

        self.series.name = "JF HH"
        self.series.save(update_fields=["name"])
        moderator_series = MeetingSeries.objects.create(name="JF VB 2")
        SeriesAccess.objects.create(
            user=self.user, series=moderator_series, role=SeriesAccess.ROLE_MODERATOR
        )
        moderator_topic = Topic.objects.create(title="Moderator-Thema", series=moderator_series)
        AuditEvent.objects.create(
            topic=self.topic, actor=self.user, action="updated", summary="Änderung aus JF HH"
        )
        AuditEvent.objects.create(
            topic=moderator_topic, actor=self.user, action="updated", summary="Änderung aus JF VB 2"
        )
        foreign_topic_meeting = Meeting.objects.create(series=moderator_series, date="2026-12-01")
        AuditEvent.objects.create(
            topic=self.topic, meeting=foreign_topic_meeting, actor=self.user,
            action="updated", summary="Serienübergreifender Eintrag mit JF HH-Thema",
        )
        self.client.force_login(self.user)

        response = self.client.get(reverse("audit_history"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Änderung aus JF VB 2")
        self.assertNotContains(response, "Änderung aus JF HH")
        self.assertNotContains(response, "Serienübergreifender Eintrag mit JF HH-Thema")
        self.assertNotContains(response, "JF HH")
        self.assertContains(response, "JF VB 2")
        self.assertEqual(list(response.context["series"]), [moderator_series])
        self.assertEqual(list(response.context["topics"]), [moderator_topic])
        # A moderator must still see changes to their topic even when the
        # linked meeting belongs to a series where they are only a participant.
        participant_meeting = Meeting.objects.create(series=self.series, date="2026-12-08")
        AuditEvent.objects.create(
            topic=moderator_topic, meeting=participant_meeting, actor=self.user,
            action="updated", summary="Änderung am moderierten Thema mit fremder Besprechung",
        )
        response = self.client.get(reverse("audit_history"))
        self.assertContains(response, "Änderung am moderierten Thema mit fremder Besprechung")


    def test_new_events_are_scoped_to_their_meeting_or_topic_series(self):
        from .audit import record_event

        moderator_series = MeetingSeries.objects.create(name="Moderierte Reihe")
        foreign_series = MeetingSeries.objects.create(name="Fremde Reihe")
        SeriesAccess.objects.create(
            user=self.user, series=moderator_series, role=SeriesAccess.ROLE_MODERATOR
        )
        meeting = Meeting.objects.create(series=moderator_series, date="2026-12-15")
        foreign_topic = Topic.objects.create(title="Thema aus fremder Reihe", series=foreign_series)

        meeting_event = record_event(
            actor=self.user, action="updated", summary="Änderung an Besprechung",
            topic=foreign_topic, meeting=meeting,
        )
        topic_event = record_event(
            actor=self.user, action="updated", summary="Eigenständige Themenänderung",
            topic=Topic.objects.create(title="Thema der moderierten Reihe", series=moderator_series),
        )
        unrelated_event = record_event(
            actor=self.user, action="updated", summary="Änderung aus fremder Reihe",
            topic=foreign_topic,
        )

        self.assertEqual(meeting_event.series, moderator_series)
        self.assertEqual(topic_event.series, moderator_series)
        self.assertEqual(unrelated_event.series, foreign_series)

        self.client.force_login(self.user)
        response = self.client.get(reverse("audit_history"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Änderung an Besprechung")
        self.assertContains(response, "Eigenständige Themenänderung")
        self.assertNotContains(response, "Änderung aus fremder Reihe")

    def test_history_renders_escaped_newlines_as_line_breaks(self):
        from .models import AuditEvent

        SeriesAccess.objects.filter(user=self.user, series=self.series).update(
            role=SeriesAccess.ROLE_MODERATOR
        )
        AuditEvent.objects.create(
            topic=self.topic,
            actor=self.user,
            action="updated",
            summary="Erste Zeile\\nZweite Zeile",
            changes={"Beschreibung": {"vorher": "Vorher\\nText", "nachher": "Nachher\\nText"}},
        )
        self.client.force_login(self.user)

        response = self.client.get(reverse("audit_history"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<p>Erste Zeile<br>Zweite Zeile</p>", html=True)
        self.assertContains(response, "Vorher<br>Text")
        self.assertNotContains(response, "\\n")


class TopicTaskManagementTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="owner", password="strong-test-password")
        self.member = User.objects.create_user(username="member", password="strong-test-password")
        self.series = MeetingSeries.objects.create(name="Aufgaben-Reihe")
        SeriesAccess.objects.create(user=self.member, series=self.series)
        self.topic = Topic.objects.create(title="Aufgabe", series=self.series)

    def test_topic_can_be_assigned_and_assignment_is_audited(self):
        self.client.force_login(self.member)
        response = self.client.post(reverse("topic_edit", args=[self.topic.pk]), {
            "title": self.topic.title,
            "description": self.topic.description,
            "due_date": "",
            "status": "open",
            "series": self.series.pk,
            "assigned_to": self.owner.pk,
        })
        self.assertRedirects(response, reverse("topic_edit", args=[self.topic.pk]))
        self.topic.refresh_from_db()
        self.assertEqual(self.topic.assigned_to, self.owner)
        from .models import AuditEvent
        event = AuditEvent.objects.get(topic=self.topic, action="updated")
        self.assertEqual(event.changes["Verantwortlich"]["vorher"], None)
        self.assertEqual(event.changes["Verantwortlich"]["nachher"], "owner")

    def test_user_can_add_comment_and_comment_is_audited(self):
        self.client.force_login(self.member)
        response = self.client.post(reverse("topic_comment_add", args=[self.topic.pk]), {
            "body": "Rückmeldung: Angebot wird bis Freitag eingeholt."
        })
        self.assertRedirects(response, reverse("topic_edit", args=[self.topic.pk]))
        from .models import AuditEvent, TopicComment
        comment = TopicComment.objects.get(topic=self.topic)
        self.assertEqual(comment.author, self.member)
        self.assertEqual(comment.body, "Rückmeldung: Angebot wird bis Freitag eingeholt.")
        self.assertTrue(AuditEvent.objects.filter(
            topic=self.topic, actor=self.member, action="comment_added"
        ).exists())

    def test_comment_endpoint_requires_login(self):
        response = self.client.post(reverse("topic_comment_add", args=[self.topic.pk]), {"body": "Test"})
        self.assertEqual(response.status_code, 302)


class MyTasksViewTests(TestCase):
    def setUp(self):
        from datetime import timedelta
        from django.utils import timezone

        self.user = User.objects.create_user(username="task-owner", password="strong-test-password")
        self.other_user = User.objects.create_user(username="other-owner", password="strong-test-password")
        self.series = MeetingSeries.objects.create(name="Meine-Aufgaben-Reihe")
        SeriesAccess.objects.create(user=self.user, series=self.series)
        today = timezone.localdate()
        self.overdue = Topic.objects.create(
            title="Überfällige Aufgabe", series=self.series, assigned_to=self.user,
            due_date=today - timedelta(days=2),
        )
        self.due_today = Topic.objects.create(
            title="Heute fällig", series=self.series, assigned_to=self.user, due_date=today,
        )
        self.no_due_date = Topic.objects.create(
            title="Ohne Fälligkeit", series=self.series, assigned_to=self.user,
        )
        Topic.objects.create(title="Aufgabe anderer Person", series=self.series, assigned_to=self.other_user)
        Topic.objects.create(title="Nicht zugewiesen", series=self.series)
        Topic.objects.create(title="Erledigt", series=self.series, assigned_to=self.user, status="done")
        Topic.objects.create(title="Archiviert", series=self.series, assigned_to=self.user, status="archived")

    def test_my_tasks_shows_only_my_open_topics_and_overdue_summary(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("my_tasks"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context["topics"]), [self.overdue, self.due_today, self.no_due_date])
        self.assertEqual(response.context["overdue_count"], 1)
        self.assertEqual(response.context["due_today_count"], 1)
        self.assertEqual(response.context["without_due_date_count"], 1)
        self.assertContains(response, "Überfällig")
        self.assertContains(response, "Heute fällig")
        self.assertNotContains(response, "Aufgabe anderer Person")
        self.assertNotContains(response, "Nicht zugewiesen")
        self.assertNotContains(response, "Erledigt")
        self.assertNotContains(response, "Archiviert")

    def test_my_tasks_requires_login(self):
        response = self.client.get(reverse("my_tasks"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)


class DashboardTopicFilterTests(TestCase):
    def setUp(self):
        from datetime import timedelta
        from django.utils import timezone

        self.user = User.objects.create_user(username="filter-user", password="strong-test-password")
        self.other_user = User.objects.create_user(username="other-filter-user", password="strong-test-password")
        self.series_a = MeetingSeries.objects.create(name="Betrieb")
        self.series_b = MeetingSeries.objects.create(name="Personal")
        SeriesAccess.objects.create(user=self.user, series=self.series_a)
        SeriesAccess.objects.create(user=self.user, series=self.series_b)
        today = timezone.localdate()
        self.topic = Topic.objects.create(
            title="Serverwartung", description="Festplatten prüfen", series=self.series_a,
            assigned_to=self.user, due_date=today + timedelta(days=2),
        )
        Topic.objects.create(title="Urlaubsplanung", series=self.series_b, assigned_to=self.other_user)
        Topic.objects.create(title="Nicht zugewiesen", series=self.series_a)

    def test_search_matches_title_description_series_and_assignee(self):
        self.client.force_login(self.user)
        for term in ["Serverwartung", "Festplatten", "Betrieb", "filter-user"]:
            response = self.client.get(reverse("dashboard"), {"q": term})
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, "Serverwartung")
            expected = [self.topic]
            if term == "Betrieb":
                expected.append(Topic.objects.get(title="Nicht zugewiesen"))
            elif term == "filter-user":
                expected.append(Topic.objects.get(title="Urlaubsplanung"))
            self.assertEqual(list(response.context["topics"]), expected)

    def test_filters_can_be_combined(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("dashboard"), {
            "status": "open", "series": self.series_a.pk,
            "assigned_to": self.user.pk, "due": "future",
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context["topics"]), [self.topic])

    def test_status_and_unassigned_filters(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("dashboard"), {"status": "all", "assigned_to": "unassigned"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context["topics"]), [
            Topic.objects.get(title="Nicht zugewiesen")
        ])



class AgendaReorderingTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="agenda-user", password="strong-test-password")
        self.client.force_login(self.user)
        self.series = MeetingSeries.objects.create(name="Agenda-Reihe")
        SeriesAccess.objects.create(user=self.user, series=self.series)
        self.meeting = Meeting.objects.create(series=self.series, date="2026-11-10")
        self.first_topic = Topic.objects.create(title="Erster Punkt", series=self.series)
        self.second_topic = Topic.objects.create(title="Zweiter Punkt", series=self.series)
        self.third_topic = Topic.objects.create(title="Dritter Punkt", series=self.series)
        self.first = AgendaItem.objects.create(meeting=self.meeting, topic=self.first_topic, position=0)
        self.second = AgendaItem.objects.create(meeting=self.meeting, topic=self.second_topic, position=1)
        self.third = AgendaItem.objects.create(meeting=self.meeting, topic=self.third_topic, position=2)

    def test_user_can_reorder_agenda_items(self):
        response = self.client.post(reverse("agenda_reorder", args=[self.meeting.pk]), {
            "item_ids": [self.third.pk, self.first.pk, self.second.pk],
        })
        self.assertRedirects(response, reverse("meeting", args=[self.meeting.pk]))
        self.assertEqual(
            list(self.meeting.agenda_items.values_list("id", flat=True)),
            [self.third.pk, self.first.pk, self.second.pk],
        )

    def test_reorder_rejects_missing_agenda_items(self):
        response = self.client.post(reverse("agenda_reorder", args=[self.meeting.pk]), {
            "item_ids": [self.first.pk, self.second.pk],
        })
        self.assertRedirects(response, reverse("meeting", args=[self.meeting.pk]))
        self.assertEqual(
            list(self.meeting.agenda_items.values_list("id", flat=True)),
            [self.first.pk, self.second.pk, self.third.pk],
        )

    def test_finalized_meeting_cannot_be_reordered(self):
        from django.utils import timezone
        self.meeting.finalized_at = timezone.now()
        self.meeting.save(update_fields=["finalized_at"])
        response = self.client.post(reverse("agenda_reorder", args=[self.meeting.pk]), {
            "item_ids": [self.third.pk, self.second.pk, self.first.pk],
        })
        self.assertRedirects(response, reverse("meeting", args=[self.meeting.pk]))
        self.assertEqual(
            list(self.meeting.agenda_items.values_list("id", flat=True)),
            [self.first.pk, self.second.pk, self.third.pk],
        )


    def test_save_all_agenda_texts_updates_multiple_items(self):
        response = self.client.post(reverse("meeting", args=[self.meeting.pk]), {
            "item_id": self.first.pk,
            "save_all_working_texts": "1",
            f"working_text_{self.first.pk}": "Erster neuer Stand",
            f"working_text_{self.second.pk}": "Zweiter neuer Stand",
            f"working_text_{self.third.pk}": "",
        })
        self.assertRedirects(response, reverse("meeting", args=[self.meeting.pk]))
        self.first.refresh_from_db()
        self.second.refresh_from_db()
        self.assertEqual(self.first.working_text, "Erster neuer Stand")
        self.assertEqual(self.second.working_text, "Zweiter neuer Stand")

    def test_save_single_agenda_text_leaves_other_items_unchanged(self):
        self.second.working_text = "Bisheriger Text"
        self.second.save(update_fields=["working_text"])
        response = self.client.post(reverse("meeting", args=[self.meeting.pk]), {
            "item_id": self.first.pk,
            "working_text": "Nur erster Punkt geändert",
        })
        self.assertRedirects(response, reverse("meeting", args=[self.meeting.pk]) + f"#agenda-item-{self.first.pk}")
        self.first.refresh_from_db()
        self.second.refresh_from_db()
        self.assertEqual(self.first.working_text, "Nur erster Punkt geändert")
        self.assertEqual(self.second.working_text, "Bisheriger Text")

    def test_meeting_page_renders_numbered_topics_and_reorder_mode_control(self):
        response = self.client.get(reverse("meeting", args=[self.meeting.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="toggle-agenda-reorder"')
        self.assertContains(response, 'class="agenda-item-number">1.')
        self.assertContains(response, 'class="agenda-item-number">2.')
        self.assertContains(response, "Reihenfolge ändern")


class ProtocolExportTests(TestCase):
    def setUp(self):
        from .models import TopicSnapshot

        self.user = User.objects.create_user(username="protocol-user", password="strong-test-password")
        self.client.force_login(self.user)
        self.series = MeetingSeries.objects.create(name="Team & Betrieb")
        SeriesAccess.objects.create(user=self.user, series=self.series)
        self.meeting = Meeting.objects.create(series=self.series, date="2026-11-06")
        self.topic = Topic.objects.create(title="Serverwartung", series=self.series)
        self.item = AgendaItem.objects.create(
            meeting=self.meeting,
            topic=self.topic,
            working_text="Wartungsfenster abstimmen.\nRückmeldung vom Team einholen.",
        )
        self.TopicSnapshot = TopicSnapshot

    def test_pdf_export_returns_pdf_attachment(self):
        response = self.client.get(reverse("protocol_pdf", args=[self.meeting.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")
        self.assertTrue(response.content.startswith(b"%PDF"))
        self.assertIn("attachment;", response["Content-Disposition"])

    def test_word_export_returns_docx_attachment(self):
        response = self.client.get(reverse("protocol_docx", args=[self.meeting.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response["Content-Type"],
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
        self.assertTrue(response.content.startswith(b"PK"))
        self.assertIn(".docx", response["Content-Disposition"])

    def test_finalized_export_uses_immutable_snapshot(self):
        from django.utils import timezone
        import zipfile
        from io import BytesIO

        self.TopicSnapshot.objects.create(
            meeting=self.meeting,
            topic_title="Historischer Titel",
            text="Gesicherter Protokolltext",
            status="open",
            topic_id=self.topic.pk,
        )
        self.meeting.finalized_at = timezone.now()
        self.meeting.save(update_fields=["finalized_at"])
        self.item.working_text = "Später geänderter Entwurf"
        self.item.save(update_fields=["working_text"])

        response = self.client.get(reverse("protocol_docx", args=[self.meeting.pk]))
        with zipfile.ZipFile(BytesIO(response.content)) as archive:
            document_xml = archive.read("word/document.xml").decode("utf-8")
        self.assertIn("Historischer Titel", document_xml)
        self.assertIn("Gesicherter Protokolltext", document_xml)
        self.assertNotIn("Später geänderter Entwurf", document_xml)

    def test_protocol_exports_require_login(self):
        self.client.logout()
        for route in ("protocol_pdf", "protocol_docx"):
            response = self.client.get(reverse(route, args=[self.meeting.pk]))
            self.assertEqual(response.status_code, 302)
            self.assertIn(reverse("login"), response.url)


class MeetingReopenTests(TestCase):
    def setUp(self):
        from django.utils import timezone
        from .models import TopicSnapshot

        self.admin = User.objects.create_user(
            username="meeting-admin", password="strong-test-password", is_staff=True
        )
        from django.contrib.auth.models import Group
        self.admin.groups.add(Group.objects.get_or_create(name="Admin")[0])
        self.client.force_login(self.admin)
        self.series = MeetingSeries.objects.create(name="Wiederöffnungs-Reihe")
        self.meeting = Meeting.objects.create(
            series=self.series, date="2026-11-06", finalized_at=timezone.now()
        )
        self.topic = Topic.objects.create(title="Wartungsplanung", series=self.series)
        self.item = AgendaItem.objects.create(
            meeting=self.meeting, topic=self.topic, working_text="Ursprünglicher Stand"
        )
        self.snapshot = TopicSnapshot.objects.create(
            meeting=self.meeting, topic_title="Wartungsplanung",
            text="Gesicherter Stand", status="open", topic_id=self.topic.pk,
        )

    def test_admin_can_reopen_meeting_and_previous_snapshot_is_audited(self):
        from .models import AuditEvent

        response = self.client.post(reverse("meeting_reopen", args=[self.meeting.pk]))

        self.assertRedirects(response, reverse("meeting", args=[self.meeting.pk]))
        self.meeting.refresh_from_db()
        self.assertIsNone(self.meeting.finalized_at)
        self.assertFalse(self.meeting.snapshots.exists())
        event = AuditEvent.objects.get(meeting=self.meeting, action="reopened")
        self.assertEqual(event.actor, self.admin)
        self.assertEqual(
            event.changes["Gesicherter Protokollstand"][0]["text"],
            "Gesicherter Stand",
        )
        self.assertEqual(event.changes["Abgeschlossen am"]["nachher"], None)

    def test_reopened_meeting_can_be_completed_again_with_a_new_snapshot(self):
        self.client.post(reverse("meeting_reopen", args=[self.meeting.pk]))
        self.item.working_text = "Überarbeiteter Stand"
        self.item.save(update_fields=["working_text"])

        response = self.client.post(reverse("finalize", args=[self.meeting.pk]))

        self.assertRedirects(response, reverse("protocol", args=[self.meeting.pk]))
        self.meeting.refresh_from_db()
        self.assertIsNotNone(self.meeting.finalized_at)
        self.assertEqual(self.meeting.snapshots.count(), 1)
        self.assertEqual(self.meeting.snapshots.get().text, "Überarbeiteter Stand")

    def test_non_staff_user_cannot_reopen_meeting(self):
        member = User.objects.create_user(username="meeting-member", password="strong-test-password")
        self.client.force_login(member)

        response = self.client.post(reverse("meeting_reopen", args=[self.meeting.pk]))

        self.assertEqual(response.status_code, 403)
        self.meeting.refresh_from_db()
        self.assertIsNotNone(self.meeting.finalized_at)

    def test_get_request_cannot_reopen_meeting(self):
        response = self.client.get(reverse("meeting_reopen", args=[self.meeting.pk]))
        self.assertEqual(response.status_code, 403)
        self.meeting.refresh_from_db()
        self.assertIsNotNone(self.meeting.finalized_at)


class MeetingParticipantTests(TestCase):
    def setUp(self):
        self.organizer = User.objects.create_user(username="organizer", password="strong-test-password")
        self.first = User.objects.create_user(
            username="first-attendee", first_name="Anna", last_name="Beispiel",
            password="strong-test-password",
        )
        self.second = User.objects.create_user(
            username="second-attendee", first_name="Ben", last_name="Muster",
            password="strong-test-password",
        )
        self.series = MeetingSeries.objects.create(name="Teilnehmer-Reihe")
        SeriesAccess.objects.create(user=self.organizer, series=self.series)
        self.meeting = Meeting.objects.create(series=self.series, date="2026-11-06")
        self.client.force_login(self.organizer)

    def test_user_can_select_multiple_meeting_participants(self):
        response = self.client.post(
            reverse("meeting", args=[self.meeting.pk]),
            {
                "save_participants": "1",
                "participants": [str(self.first.pk), str(self.second.pk)],
            },
        )
        self.assertRedirects(response, reverse("meeting", args=[self.meeting.pk]))
        self.assertQuerySetEqual(
            self.meeting.participants.order_by("pk"),
            [self.first, self.second],
        )

    def test_finalized_meeting_participant_list_is_locked(self):
        from django.utils import timezone

        self.meeting.participants.add(self.first)
        self.meeting.finalized_at = timezone.now()
        self.meeting.save(update_fields=["finalized_at"])
        response = self.client.post(
            reverse("meeting", args=[self.meeting.pk]),
            {"save_participants": "1", "participants": [str(self.second.pk)]},
        )
        self.assertRedirects(response, reverse("meeting", args=[self.meeting.pk]))
        self.assertQuerySetEqual(self.meeting.participants.all(), [self.first])

    def test_participants_are_displayed_in_html_protocol(self):
        self.meeting.participants.add(self.first, self.second)
        response = self.client.get(reverse("protocol", args=[self.meeting.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Anna Beispiel")
        self.assertContains(response, "Ben Muster")

    def test_participants_are_included_in_word_export(self):
        import zipfile
        from io import BytesIO

        self.meeting.participants.add(self.first)
        response = self.client.get(reverse("protocol_docx", args=[self.meeting.pk]))
        with zipfile.ZipFile(BytesIO(response.content)) as archive:
            document_xml = archive.read("word/document.xml").decode("utf-8")
        self.assertIn("Anna Beispiel", document_xml)


class DashboardUpcomingMeetingsTests(TestCase):
    def setUp(self):
        from datetime import timedelta
        from django.utils import timezone

        self.user = User.objects.create_user(username="dashboard-user", password="strong-test-password")
        self.client.force_login(self.user)
        self.series_a = MeetingSeries.objects.create(name="Reihe Alpha")
        self.series_b = MeetingSeries.objects.create(name="Reihe Beta")
        SeriesAccess.objects.create(user=self.user, series=self.series_a)
        SeriesAccess.objects.create(user=self.user, series=self.series_b)
        today = timezone.localdate()
        self.a_dates = [today + timedelta(days=offset) for offset in (1, 3, 5)]
        self.b_dates = [today + timedelta(days=offset) for offset in (2, 4, 6)]
        for date in self.a_dates:
            Meeting.objects.create(series=self.series_a, date=date)
        for date in self.b_dates:
            Meeting.objects.create(series=self.series_b, date=date)
        Meeting.objects.create(series=self.series_a, date=today - timedelta(days=1))

    def test_dashboard_shows_only_two_nearest_future_meetings_per_series(self):
        response = self.client.get(reverse("dashboard"))

        self.assertEqual(response.status_code, 200)
        meetings = list(response.context["meetings"])
        self.assertEqual(len(meetings), 4)
        self.assertEqual(
            [(meeting.series_id, meeting.date) for meeting in meetings],
            [
                (self.series_a.pk, self.a_dates[0]),
                (self.series_b.pk, self.b_dates[0]),
                (self.series_a.pk, self.a_dates[1]),
                (self.series_b.pk, self.b_dates[1]),
            ],
        )
        self.assertNotIn(self.a_dates[2], [meeting.date for meeting in meetings])
        self.assertNotIn(self.b_dates[2], [meeting.date for meeting in meetings])

    def test_dashboard_upcoming_meetings_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)


class MeetingSeriesManagementTests(TestCase):
    def setUp(self):
        from datetime import timedelta
        from django.utils import timezone

        self.admin = User.objects.create_user(
            username="series-admin", password="strong-test-password", is_staff=True
        )
        from django.contrib.auth.models import Group
        self.admin.groups.add(Group.objects.get_or_create(name="Admin")[0])
        self.client.force_login(self.admin)
        self.today = timezone.localdate()
        self.series = MeetingSeries.objects.create(
            name="Planungsreihe", recurrence="weekly", weekday=0,
            start_date=self.today,
        )
        self.meeting = Meeting.objects.create(
            series=self.series, date=self.today + timedelta(days=14)
        )

    def series_payload(self, **overrides):
        data = {
            "name": self.series.name,
            "description": self.series.description,
            "active": "on",
            "recurrence": self.series.recurrence,
            "recurrence_interval": "1",
            "weekday": "2",
            "start_date": self.series.start_date.isoformat(),
            "end_date": "",
        }
        data.update(overrides)
        return data

    def test_changing_series_weekday_moves_future_unfinalized_meetings(self):
        from datetime import timedelta

        response = self.client.post(
            reverse("series_edit", args=[self.series.pk]), self.series_payload()
        )
        self.assertRedirects(response, reverse("series_admin"))
        self.meeting.refresh_from_db()
        self.series.refresh_from_db()
        self.assertEqual(self.meeting.date, self.today + timedelta(days=16))
        self.assertEqual(self.series.weekday, 2)

    def test_individual_meeting_can_be_moved_without_moving_other_dates(self):
        from datetime import timedelta

        other = Meeting.objects.create(
            series=self.series, date=self.today + timedelta(days=21)
        )
        new_date = self.today + timedelta(days=18)
        response = self.client.post(
            reverse("meeting_edit", args=[self.meeting.pk]),
            {"date": new_date.isoformat()},
        )
        self.assertRedirects(response, reverse("meeting", args=[self.meeting.pk]))
        self.meeting.refresh_from_db()
        other.refresh_from_db()
        self.assertEqual(self.meeting.date, new_date)
        self.assertEqual(other.date, self.today + timedelta(days=21))

    def test_individual_meeting_delete_keeps_series(self):
        response = self.client.post(reverse("meeting_delete", args=[self.meeting.pk]))
        self.assertRedirects(response, reverse("series_admin"))
        self.assertFalse(Meeting.objects.filter(pk=self.meeting.pk).exists())
        self.assertTrue(MeetingSeries.objects.filter(pk=self.series.pk).exists())

    def test_series_delete_removes_future_drafts_but_preserves_completed_protocols(self):
        from datetime import timedelta
        from django.utils import timezone
        from .models import TopicSnapshot

        completed = Meeting.objects.create(
            series=self.series, date=self.today - timedelta(days=7),
            finalized_at=timezone.now(),
        )
        snapshot = TopicSnapshot.objects.create(
            meeting=completed, topic_title="Historischer Punkt",
            text="Gesicherter Protokolltext", status="open", topic_id=999,
        )
        topic = Topic.objects.create(title="Bleibt erhalten", series=self.series)

        response = self.client.post(reverse("series_delete", args=[self.series.pk]))

        self.assertRedirects(response, reverse("series_admin"))
        self.assertFalse(MeetingSeries.objects.filter(pk=self.series.pk).exists())
        self.assertFalse(Meeting.objects.filter(pk=self.meeting.pk).exists())
        completed.refresh_from_db()
        topic.refresh_from_db()
        self.assertIsNone(completed.series_id)
        self.assertTrue(completed.snapshots.filter(pk=snapshot.pk).exists())
        self.assertIsNone(topic.series_id)
        protocol_response = self.client.get(reverse("protocol", args=[completed.pk]))
        self.assertEqual(protocol_response.status_code, 200)
        self.assertContains(protocol_response, "Gelöschte Besprechungsreihe")
        meeting_response = self.client.get(reverse("meeting", args=[completed.pk]))
        self.assertEqual(meeting_response.status_code, 200)

    def test_series_delete_can_also_remove_completed_meetings_when_selected(self):
        from datetime import timedelta
        from django.utils import timezone
        from .models import TopicSnapshot

        completed = Meeting.objects.create(
            series=self.series, date=self.today - timedelta(days=7),
            finalized_at=timezone.now(),
        )
        snapshot = TopicSnapshot.objects.create(
            meeting=completed, topic_title="Historischer Punkt",
            text="Gesicherter Protokolltext", status="open", topic_id=999,
        )

        response = self.client.post(
            reverse("series_delete", args=[self.series.pk]),
            {"delete_completed": "on"},
        )

        self.assertRedirects(response, reverse("series_admin"))
        self.assertFalse(MeetingSeries.objects.filter(pk=self.series.pk).exists())
        self.assertFalse(Meeting.objects.filter(pk=completed.pk).exists())
        self.assertFalse(TopicSnapshot.objects.filter(pk=snapshot.pk).exists())
        self.assertFalse(Meeting.objects.filter(pk=self.meeting.pk).exists())

    def test_next_meeting_can_be_deleted_from_series_overview(self):
        response = self.client.get(reverse("series_admin"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Termin löschen")

        response = self.client.post(reverse("meeting_delete", args=[self.meeting.pk]))
        self.assertRedirects(response, reverse("series_admin"))
        self.assertFalse(Meeting.objects.filter(pk=self.meeting.pk).exists())
        self.assertTrue(MeetingSeries.objects.filter(pk=self.series.pk).exists())

    def test_empty_series_can_be_deleted(self):
        self.meeting.delete()
        response = self.client.post(reverse("series_delete", args=[self.series.pk]))
        self.assertRedirects(response, reverse("series_admin"))
        self.assertFalse(MeetingSeries.objects.filter(pk=self.series.pk).exists())

    def test_non_admin_cannot_manage_series(self):
        member = User.objects.create_user(username="series-member", password="strong-test-password")
        self.client.force_login(member)
        response = self.client.get(reverse("series_admin"))
        self.assertEqual(response.status_code, 403)
        self.assertTrue(MeetingSeries.objects.filter(pk=self.series.pk).exists())

    def test_series_overview_shows_next_appointment_and_collapses_the_rest(self):
        from datetime import timedelta

        next_date = self.today + timedelta(days=14)
        later_date = self.today + timedelta(days=28)
        later = Meeting.objects.create(series=self.series, date=later_date)

        response = self.client.get(reverse("series_admin"))

        self.assertEqual(response.status_code, 200)
        series_in_context = response.context["series"][0]
        self.assertEqual(series_in_context.next_meeting.pk, self.meeting.pk)
        self.assertEqual([item.pk for item in series_in_context.other_meetings], [later.pk])
        self.assertContains(response, "Nächster Termin:")
        self.assertContains(response, "Alle weiteren Termine anzeigen (1)")
        self.assertContains(response, "<details")
        self.assertContains(response, next_date.strftime("%d.%m.%Y"))

    def test_series_overview_shows_meeting_today_as_the_primary_appointment(self):
        today_meeting = Meeting.objects.create(series=self.series, date=self.today)
        response = self.client.get(reverse("series_admin"))
        self.assertEqual(response.status_code, 200)
        series_in_context = response.context["series"][0]
        self.assertEqual(series_in_context.next_meeting.pk, today_meeting.pk)

    def test_finalized_meeting_cannot_be_moved_or_deleted(self):
        from datetime import timedelta
        from django.utils import timezone

        self.meeting.finalized_at = timezone.now()
        self.meeting.save(update_fields=["finalized_at"])
        response = self.client.post(
            reverse("meeting_edit", args=[self.meeting.pk]),
            {"date": (self.today + timedelta(days=30)).isoformat()},
        )
        self.assertRedirects(response, reverse("meeting", args=[self.meeting.pk]))
        self.client.post(reverse("meeting_delete", args=[self.meeting.pk]))
        self.assertTrue(Meeting.objects.filter(pk=self.meeting.pk).exists())



class MeetingSeriesSchedulingTests(TestCase):
    def setUp(self):
        from datetime import timedelta
        from django.utils import timezone
        self.today = timezone.localdate()
        self.admin = User.objects.create_user(username="series-scheduler-admin", password="strong-test-password", is_staff=True)
        from django.contrib.auth.models import Group
        self.admin.groups.add(Group.objects.get_or_create(name="Admin")[0])
        self.client.force_login(self.admin)
        self.series = MeetingSeries.objects.create(
            name="Rhythmusreihe", recurrence="weekly", recurrence_interval=4,
            weekday=0, start_date=self.today,
            end_date=self.today + timedelta(days=7),
        )
        self.meeting = Meeting.objects.create(
            series=self.series, date=self.today + timedelta(days=14)
        )

    def test_four_week_recurrence_generates_all_dates_to_end(self):
        from datetime import timedelta
        from .services import generate_meetings
        start = self.today + timedelta(days=(0 - self.today.weekday()) % 7)
        self.series.start_date = start
        self.series.end_date = start + timedelta(days=70)
        self.series.weekday = 0
        self.series.recurrence = "weekly"
        self.series.recurrence_interval = 4
        self.series.save()
        self.meeting.delete()
        generate_meetings(self.series)
        dates = list(
            Meeting.objects.filter(series=self.series).order_by("date").values_list("date", flat=True)
        )
        self.assertEqual(dates, [start, start + timedelta(days=28), start + timedelta(days=56)])

    def test_two_month_recurrence_keeps_same_weekday_occurrence(self):
        from datetime import timedelta
        from .services import generate_meetings, _monthly_weekday
        start = self.today + timedelta(days=(0 - self.today.weekday()) % 7)
        end = start + timedelta(days=150)
        self.series.start_date = start
        self.series.end_date = end
        self.series.weekday = 0
        self.series.recurrence = "monthly"
        self.series.recurrence_interval = 2
        self.series.save()
        self.meeting.delete()
        generate_meetings(self.series)
        expected = [start]
        cursor = start
        occurrence = (start.day - 1) // 7 + 1
        while True:
            month_index = cursor.year * 12 + cursor.month - 1 + 2
            year, month_zero = divmod(month_index, 12)
            cursor = _monthly_weekday(year, month_zero + 1, 0, occurrence)
            if cursor > end:
                break
            expected.append(cursor)
        dates = list(
            Meeting.objects.filter(series=self.series).order_by("date").values_list("date", flat=True)
        )
        self.assertEqual(dates, expected)

    def test_new_series_form_defaults_to_next_selected_weekday_and_next_year_end(self):
        from datetime import date, timedelta
        from django.utils import timezone
        from .forms import SeriesForm
        today = timezone.localdate()
        form = SeriesForm()
        expected_start = today + timedelta(days=(0 - today.weekday()) % 7)
        self.assertEqual(form.initial["start_date"], expected_start)
        self.assertEqual(form.initial["end_date"], date(today.year + 1, 12, 31))

    def test_extend_adds_dates_through_end_of_following_year(self):
        from datetime import date, timedelta
        self.series.end_date = self.today + timedelta(days=1)
        self.series.save(update_fields=["end_date"])
        response = self.client.post(reverse("series_extend", args=[self.series.pk]))
        expected_redirect = f"{reverse('series_admin')}?expanded={self.series.pk}#series-{self.series.pk}"
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], expected_redirect)
        self.series.refresh_from_db()
        self.assertEqual(self.series.end_date, date(self.today.year + 1, 12, 31))
        self.assertTrue(Meeting.objects.filter(series=self.series, date__gt=self.today + timedelta(days=1)).exists())
        count_after_first_extension = Meeting.objects.filter(series=self.series).count()

        second_response = self.client.post(reverse("series_extend", args=[self.series.pk]))
        self.assertEqual(second_response.status_code, 302)
        self.assertEqual(Meeting.objects.filter(series=self.series).count(), count_after_first_extension)

    def test_meeting_date_form_uses_german_day_month_year_format(self):
        from .forms import MeetingDateForm
        form = MeetingDateForm(instance=self.meeting)
        self.assertIn(self.meeting.date.strftime("%d.%m.%Y"), str(form["date"]))
        submitted = MeetingDateForm(data={"date": "05.12.2026"}, instance=self.meeting)
        self.assertTrue(submitted.is_valid(), submitted.errors)
        self.assertEqual(submitted.cleaned_data["date"].isoformat(), "2026-12-05")

    def test_reset_moves_agenda_items_to_next_new_meeting_and_preserves_completed_protocols(self):
        from datetime import timedelta
        from django.utils import timezone
        from .models import TopicSnapshot
        topic = Topic.objects.create(title="Mitnehmen", series=self.series, due_date=self.meeting.date)
        AgendaItem.objects.create(meeting=self.meeting, topic=topic, working_text="Aktueller Stand", position=3)
        completed = Meeting.objects.create(
            series=self.series, date=self.today - timedelta(days=7), finalized_at=timezone.now()
        )
        snapshot = TopicSnapshot.objects.create(
            meeting=completed, topic_title="Historischer Protokollpunkt",
            text="Gesicherter Text", status="open", topic_id=9876,
        )
        response = self.client.post(reverse("series_reset_meetings", args=[self.series.pk]))
        self.assertRedirects(response, reverse("series_edit", args=[self.series.pk]))
        completed.refresh_from_db()
        self.assertTrue(completed.snapshots.filter(pk=snapshot.pk).exists())
        next_meeting = Meeting.objects.filter(
            series=self.series, finalized_at__isnull=True, date__gte=self.today
        ).order_by("date").first()
        self.assertIsNotNone(next_meeting)
        moved = AgendaItem.objects.get(meeting=next_meeting, topic=topic)
        self.assertEqual(moved.working_text, "Aktueller Stand")
        self.assertEqual(moved.position, 3)
        self.assertTrue(moved.carried_forward)
        self.assertFalse(Meeting.objects.filter(pk=self.meeting.pk).exists())

    def test_moderator_sees_and_manages_only_assigned_moderator_series(self):
        moderator = User.objects.create_user(username="series-limited-moderator", password="strong-test-password")
        other = MeetingSeries.objects.create(name="Fremde Reihe")
        SeriesAccess.objects.create(user=moderator, series=self.series, role=SeriesAccess.ROLE_MODERATOR)
        SeriesAccess.objects.create(user=moderator, series=other, role=SeriesAccess.ROLE_PARTICIPANT)
        self.client.force_login(moderator)
        response = self.client.get(reverse("series_admin"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Rhythmusreihe")
        self.assertNotContains(response, "Fremde Reihe")
        denied = self.client.get(reverse("series_edit", args=[other.pk]))
        self.assertEqual(denied.status_code, 403)
        denied_extend = self.client.post(reverse("series_extend", args=[other.pk]))
        self.assertEqual(denied_extend.status_code, 403)



class MeetingParticipantDefaultsTests(TestCase):
    def setUp(self):
        self.assigned = User.objects.create_user(
            username="assigned", first_name="Ada", last_name="Lovelace",
            password="strong-test-password",
        )
        self.unassigned = User.objects.create_user(
            username="unassigned", password="strong-test-password",
        )
        self.series = MeetingSeries.objects.create(name="Teilnehmer-Reihe")
        SeriesAccess.objects.create(user=self.assigned, series=self.series)
        self.meeting = Meeting.objects.create(series=self.series, date="2026-12-15")
        self.client.force_login(self.assigned)

    def test_series_assignees_are_preselected_on_first_meeting_open(self):
        response = self.client.get(reverse("meeting", args=[self.meeting.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            list(self.meeting.participants.values_list("pk", flat=True)),
            [self.assigned.pk],
        )
        self.meeting.refresh_from_db()
        self.assertTrue(self.meeting.participants_initialized)
        self.assertContains(response, "participant-menu-panel")
        self.assertEqual(
            list(response.context["participant_form"]["participants"].value()),
            [self.assigned.pk],
        )

    def test_manually_cleared_participant_list_stays_empty(self):
        self.client.get(reverse("meeting", args=[self.meeting.pk]))
        response = self.client.post(
            reverse("meeting", args=[self.meeting.pk]),
            {"save_participants": "1"},
        )

        self.assertEqual(response.status_code, 302)
        self.meeting.refresh_from_db()
        self.assertTrue(self.meeting.participants_initialized)
        self.assertFalse(self.meeting.participants.exists())
        self.client.get(reverse("meeting", args=[self.meeting.pk]))
        self.assertFalse(self.meeting.participants.exists())

    def test_existing_participants_are_not_overwritten_by_series_defaults(self):
        self.meeting.participants.add(self.unassigned)

        self.client.get(reverse("meeting", args=[self.meeting.pk]))

        self.assertEqual(
            list(self.meeting.participants.values_list("pk", flat=True)),
            [self.unassigned.pk],
        )

    def test_participant_list_can_add_non_series_user_and_remove_series_user(self):
        self.client.get(reverse("meeting", args=[self.meeting.pk]))

        response = self.client.post(
            reverse("meeting", args=[self.meeting.pk]),
            {"save_participants": "1", "participants": [str(self.unassigned.pk)]},
        )

        self.assertEqual(response.status_code, 302)
        self.meeting.refresh_from_db()
        self.assertEqual(
            list(self.meeting.participants.values_list("pk", flat=True)),
            [self.unassigned.pk],
        )

    def test_readers_are_displayed_in_the_middle_as_non_participants(self):
        reader = User.objects.create_user(
            username="series-reader", first_name="Lese", last_name="Person",
            password="strong-test-password",
        )
        SeriesAccess.objects.create(user=reader, series=self.series, role=SeriesAccess.ROLE_READER)

        response = self.client.get(reverse("meeting", args=[self.meeting.pk]))

        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        series_section = content.index("Der Besprechungsserie zugeordnet")
        reader_section = content.index("Leser*innen (optional als Teilnehmer)")
        other_section = content.index("Weitere Nutzer")
        self.assertLess(series_section, reader_section)
        self.assertLess(reader_section, other_section)
        self.assertIn("Lese Person", content)
        self.assertIn(f'value="{reader.pk}"', content)
        self.assertNotRegex(content, rf'value="{reader.pk}"[^>]*checked')
        self.assertFalse(self.meeting.participants.filter(pk=reader.pk).exists())

    def test_reader_can_be_selected_as_an_optional_meeting_participant(self):
        reader = User.objects.create_user(
            username="optional-reader", first_name="Optionale", last_name="Leserin",
            password="strong-test-password",
        )
        SeriesAccess.objects.create(user=reader, series=self.series, role=SeriesAccess.ROLE_READER)

        response = self.client.post(
            reverse("meeting", args=[self.meeting.pk]),
            {"save_participants": "1", "participants": [str(reader.pk)]},
        )

        self.assertEqual(response.status_code, 302)
        self.meeting.refresh_from_db()
        self.assertTrue(self.meeting.participants.filter(pk=reader.pk).exists())
        meeting_response = self.client.get(reverse("meeting", args=[self.meeting.pk]))
        self.assertRegex(meeting_response.content.decode(), rf'value="{reader.pk}"[^>]*checked')

    def test_series_members_are_listed_before_other_active_users(self):
        response = self.client.get(reverse("meeting", args=[self.meeting.pk]))

        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertLess(
            content.index("Der Besprechungsserie zugeordnet"),
            content.index("Weitere Nutzer"),
        )
        self.assertLess(
            content.index("Ada Lovelace</span>"),
            content.index("unassigned"),
        )
        self.assertContains(response, 'type="checkbox"')
        self.assertContains(response, "participant-menu-panel")
        self.assertContains(response, "Der Besprechungsserie zugeordnet")
        self.assertContains(response, "Weitere Nutzer")


    def test_meeting_actions_are_grouped_in_top_menu_and_participants_use_dropdown(self):
        topic = Topic.objects.create(title="Menütest", series=self.series)
        AgendaItem.objects.create(meeting=self.meeting, topic=topic, working_text="Text")
        response = self.client.get(reverse("meeting", args=[self.meeting.pk]))

        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn('aria-label="Aktionen für diese Besprechung"', content)
        self.assertIn("Teilnehmer", content)
        self.assertIn("Protokoll / Drucken", content)
        self.assertIn('id="agenda-reorder-form"', content)
        self.assertIn("recordOrderChange", content)
        self.assertIn("orderForm.requestSubmit()", content)
        self.assertIn('id="save-agenda-order"', content)
        self.assertIn('id="agenda-save-choice-dialog"', content)
        self.assertIn("Alle Änderungen speichern", content)
        self.assertIn("Nur diesen Punkt speichern", content)
        self.assertNotIn("window.confirm", content)
        self.assertIn('move-up"', content)
        self.assertIn('move-down"', content)
        self.assertNotIn("Reihenfolge speichern", content)
        self.assertIn(">Besprechung abschließen</button>", content)
        self.assertNotIn("Protokollstand sichern", content)
        self.assertIn("meeting-menu-participants", content)
        self.assertIn("participant-menu-panel", content)
        self.assertNotIn('<section class="card participant-card"', content)
        self.assertNotIn("Teilnehmer anpassen", content)
        self.assertIn('type="checkbox"', content)

    def test_finalized_meeting_hides_editing_and_completion_actions(self):
        from django.utils import timezone

        self.meeting.finalized_at = timezone.now()
        self.meeting.save(update_fields=["finalized_at"])
        response = self.client.get(reverse("meeting", args=[self.meeting.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Teilnehmer auswählen oder ändern")
        self.assertNotContains(response, "Reihenfolge speichern")
        self.assertNotContains(response, "Besprechung abschließen")
        self.assertContains(response, "Protokoll / Drucken")


class UserShortDescriptionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="display-user",
            first_name="Name",
            password="strong-test-password",
        )
        self.series = MeetingSeries.objects.create(name="Kurzbeschreibung-Reihe")
        SeriesAccess.objects.create(user=self.user, series=self.series)
        self.meeting = Meeting.objects.create(series=self.series, date="2026-12-20")
        self.meeting.participants.add(self.user)
        self.client.force_login(self.user)

    def test_short_description_does_not_change_account_name(self):
        from .models import UserProfile
        from .user_display import user_display_name

        UserProfile.objects.create(user=self.user, short_description="01/22")

        self.user.refresh_from_db()
        self.assertEqual(self.user.username, "display-user")
        self.assertEqual(user_display_name(self.user), "Name")
        self.assertEqual(user_display_name(self.user, include_short_description=True), "Name (01/22)")

    def test_short_description_appears_in_participant_dropdown_and_protocol(self):
        from .models import UserProfile

        UserProfile.objects.create(user=self.user, short_description="01/22")

        meeting_response = self.client.get(reverse("meeting", args=[self.meeting.pk]))
        self.assertEqual(meeting_response.status_code, 200)
        self.assertContains(meeting_response, "Name (01/22)")

        protocol_response = self.client.get(reverse("protocol", args=[self.meeting.pk]))
        self.assertEqual(protocol_response.status_code, 200)
        self.assertContains(protocol_response, "Name (01/22)")

    def test_short_description_appears_in_word_protocol_export(self):
        import zipfile
        from io import BytesIO
        from .models import UserProfile

        UserProfile.objects.create(user=self.user, short_description="01/22")
        response = self.client.get(reverse("protocol_docx", args=[self.meeting.pk]))

        with zipfile.ZipFile(BytesIO(response.content)) as archive:
            document_xml = archive.read("word/document.xml").decode("utf-8")
        self.assertIn("Name (01/22)", document_xml)

    def test_dashboard_greeting_and_sidebar_use_full_name(self):
        self.user.last_name = "Mustermann"
        self.user.save(update_fields=["last_name"])
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Willkommen, Name Mustermann")
        self.assertContains(response, '<span class="username">Name Mustermann</span>', html=True)
        self.assertNotContains(response, "Willkommen, display-user")

    def test_user_display_falls_back_to_username_when_name_is_missing(self):
        from .user_display import user_display_name, user_display_name_with_login
        self.assertEqual(user_display_name(self.user), "Name")
        self.user.first_name = ""
        self.user.save(update_fields=["first_name"])
        self.assertEqual(user_display_name(self.user), "display-user")
        self.assertEqual(user_display_name_with_login(self.user), "display-user")

    def test_user_admin_exposes_editable_short_description_and_login_identifier(self):
        from .models import UserProfile

        UserProfile.objects.create(user=self.user, short_description="01/22")
        self.user.email = "private@example.com"
        self.user.save(update_fields=["email"])
        admin_user = User.objects.create_superuser(
            username="profile-admin", password="strong-test-password", email="admin@example.com"
        )
        self.client.force_login(admin_user)
        response = self.client.get(reverse("admin:auth_user_change", args=[self.user.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Kurzbeschreibung")
        self.assertContains(response, "01/22")
        changelist = self.client.get(reverse("admin:auth_user_changelist"))
        self.assertEqual(changelist.status_code, 200)
        self.assertContains(changelist, "Name (display-user)")
        self.assertNotContains(changelist, "private@example.com")



class ProtocolEmailTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="protocol-owner",
            first_name="Protokoll",
            last_name="Nutzer",
            email="protokoll@example.com",
            password="strong-test-password",
        )
        self.series = MeetingSeries.objects.create(name="Strategierunde")
        self.meeting = Meeting.objects.create(series=self.series, date="2026-12-20")
        SeriesAccess.objects.create(user=self.user, series=self.series)
        self.client.force_login(self.user)

    def test_protocol_email_is_prefilled_for_all_series_assignees(self):
        from urllib.parse import parse_qs, urlsplit

        second_user = User.objects.create_user(
            username="second-series-user",
            email="zweite-person@example.com",
            password="strong-test-password",
        )
        SeriesAccess.objects.create(user=second_user, series=self.series)
        # A series assignment without an email address cannot be added to a mail draft.
        no_email_user = User.objects.create_user(
            username="no-email-user",
            password="strong-test-password",
        )
        SeriesAccess.objects.create(user=no_email_user, series=self.series)
        response = self.client.get(reverse("protocol", args=[self.meeting.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Protokoll verschicken")
        self.assertContains(response, "meeting-action-menu")
        self.assertContains(response, "meeting-menu-link")
        self.assertContains(response, "meeting-menu-button")
        mailto = response.context["protocol_mailto"]
        parsed = urlsplit(mailto)
        self.assertEqual(parsed.scheme, "mailto")
        self.assertEqual(
            parsed.path,
            "protokoll@example.com,zweite-person@example.com",
        )
        query = parse_qs(parsed.query)
        self.assertEqual(
            query["subject"][0],
            "Protokoll Strategierunde 20.12.2026",
        )
        protocol_url = response.wsgi_request.build_absolute_uri(
            reverse("protocol", args=[self.meeting.pk])
        )
        self.assertEqual(
            query["body"][0],
            "Hallo zusammen,\n\n"
            "das Protokoll für die Sitzung Strategierunde am 20.12.2026 "
            f"ist unter {protocol_url} verfügbar.\n\n",
        )

    def test_protocol_email_button_is_unavailable_without_series_recipients(self):
        self.user.email = ""
        self.user.save(update_fields=["email"])
        response = self.client.get(reverse("protocol", args=[self.meeting.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "keine E-Mail-Adressen hinterlegt")
        self.assertEqual(response.context["protocol_mail_recipients"], [])


class MeetingAgendaEnhancementTests(TestCase):
    def setUp(self):
        from datetime import date
        self.user = User.objects.create_user(username="agenda-editor", password="strong-test-password")
        self.series_a = MeetingSeries.objects.create(name="Gremium A")
        self.series_b = MeetingSeries.objects.create(name="Gremium B")
        SeriesAccess.objects.create(user=self.user, series=self.series_a)
        SeriesAccess.objects.create(user=self.user, series=self.series_b)
        self.meeting = Meeting.objects.create(series=self.series_a, date=date(2026, 12, 1))
        self.target_meeting = Meeting.objects.create(series=self.series_b, date=date(2027, 1, 12))
        self.client.force_login(self.user)

    def test_new_agenda_topic_can_be_created_from_meeting_page(self):
        response = self.client.post(
            reverse("meeting", args=[self.meeting.pk]),
            {"add_agenda_topic": "1", "title": "Neuer Tagesordnungspunkt", "working_text": "Ein erster Sachstand"},
        )
        self.assertRedirects(response, reverse("meeting", args=[self.meeting.pk]))
        topic = Topic.objects.get(title="Neuer Tagesordnungspunkt")
        self.assertEqual(topic.series, self.series_a)
        self.assertEqual(topic.due_date, self.meeting.date)
        item = AgendaItem.objects.get(meeting=self.meeting, topic=topic)
        self.assertEqual(item.working_text, "Ein erster Sachstand")

    def test_topic_suggestions_return_matching_accessible_topics(self):
        Topic.objects.create(title="Digitalisierung Haushalt", series=self.series_a)
        Topic.objects.create(title="Digitalisierung Schule", series=self.series_b)
        response = self.client.get(reverse("topic_suggestions"), {"q": "Digitalisierung"})
        self.assertEqual(response.status_code, 200)
        results = response.json()["results"]
        titles = [entry["title"] for entry in results]
        self.assertEqual(titles, ["Digitalisierung Haushalt", "Digitalisierung Schule"])
        self.assertEqual(
            {entry["id"] for entry in results},
            set(Topic.objects.filter(title__startswith="Digitalisierung").values_list("pk", flat=True)),
        )

    def test_existing_topic_is_added_only_to_current_agenda_without_changing_series_or_due_date(self):
        topic = Topic.objects.create(
            title="Vorhandenes Thema", series=self.series_b,
            due_date=self.target_meeting.date, description="Bisheriger Sachstand",
        )
        response = self.client.post(
            reverse("meeting", args=[self.meeting.pk]),
            {"add_existing_topic": str(topic.pk)},
        )
        self.assertRedirects(response, reverse("meeting", args=[self.meeting.pk]))
        topic.refresh_from_db()
        self.assertEqual(topic.series, self.series_b)
        self.assertEqual(topic.due_date, self.target_meeting.date)
        item = AgendaItem.objects.get(meeting=self.meeting, topic=topic)
        self.assertEqual(item.working_text, "Bisheriger Sachstand")
        self.assertFalse(AgendaItem.objects.filter(meeting=self.target_meeting, topic=topic).exists())

    def test_existing_topic_cannot_be_added_twice_to_same_agenda(self):
        topic = Topic.objects.create(title="Bereits vorhanden", series=self.series_a)
        AgendaItem.objects.create(meeting=self.meeting, topic=topic)
        response = self.client.post(
            reverse("meeting", args=[self.meeting.pk]),
            {"add_existing_topic": str(topic.pk)},
        )
        self.assertRedirects(response, reverse("meeting", args=[self.meeting.pk]))
        self.assertEqual(AgendaItem.objects.filter(meeting=self.meeting, topic=topic).count(), 1)

    def test_agenda_item_can_be_scheduled_for_selected_committee_meeting(self):
        topic = Topic.objects.create(title="Zu übertragendes Thema", series=self.series_a)
        item = AgendaItem.objects.create(meeting=self.meeting, topic=topic, working_text="Bitte erneut beraten")
        response = self.client.post(
            reverse("meeting", args=[self.meeting.pk]),
            {
                "schedule_item": str(item.pk),
                "target_series": str(self.series_b.pk),
                "target_meeting": str(self.target_meeting.pk),
            },
        )
        self.assertRedirects(response, reverse("meeting", args=[self.meeting.pk]))
        topic.refresh_from_db()
        self.assertEqual(topic.series, self.series_b)
        self.assertEqual(topic.due_date, self.target_meeting.date)
        transfer = TopicTransferHistory.objects.get(topic=topic)
        self.assertEqual(transfer.from_series, self.series_a)
        self.assertEqual(transfer.to_series, self.series_b)
        target_response = self.client.get(reverse("meeting", args=[self.target_meeting.pk]))
        self.assertEqual(target_response.status_code, 200)
        self.assertContains(target_response, "Zu übertragendes Thema")
        from .services import ensure_agenda
        later_source_meeting = Meeting.objects.create(series=self.series_a, date="2027-02-01")
        self.assertFalse(ensure_agenda(later_source_meeting).filter(topic=topic).exists())

    def test_followup_is_saved_only_with_agenda_text_and_creates_blank_target_item(self):
        topic = Topic.objects.create(title="Wiedervorlage ohne Standardtext", series=self.series_a)
        item = AgendaItem.objects.create(meeting=self.meeting, topic=topic, working_text="Besprochener Stand")
        response = self.client.post(
            reverse("meeting", args=[self.meeting.pk]),
            {
                "item_id": str(item.pk),
                "schedule_item": str(item.pk),
                "working_text": "Aktualisierter Protokolltext",
                "target_series": str(self.series_b.pk),
                "target_meeting": str(self.target_meeting.pk),
            },
        )
        self.assertRedirects(response, reverse("meeting", args=[self.meeting.pk]) + f"#agenda-item-{item.pk}")
        topic.refresh_from_db()
        item.refresh_from_db()
        target_item = AgendaItem.objects.get(meeting=self.target_meeting, topic=topic)
        self.assertEqual(topic.series, self.series_b)
        self.assertEqual(topic.due_date, self.target_meeting.date)
        self.assertEqual(item.working_text, "Aktualisierter Protokolltext")
        self.assertEqual(target_item.working_text, "")

    def test_followup_dropdowns_are_associated_with_text_save_not_autosubmitted(self):
        topic = Topic.objects.create(title="Auswahl bleibt offen", series=self.series_a)
        AgendaItem.objects.create(meeting=self.meeting, topic=topic)
        response = self.client.get(reverse("meeting", args=[self.meeting.pk]))
        content = response.content.decode()
        self.assertIn('form="agenda-text-form-', content)
        self.assertIn('name="schedule_item"', content)
        self.assertNotIn('onchange="this.form.requestSubmit()"', content)

    def test_history_includes_planned_followup_meeting_without_agenda_item(self):
        topic = Topic.objects.create(
            title="Geplante Historie", series=self.series_b, due_date=self.target_meeting.date,
        )
        AgendaItem.objects.create(meeting=self.meeting, topic=topic, working_text="Besprochen")
        response = self.client.get(reverse("agenda_topic_history", args=[self.meeting.pk, topic.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "12.01.2027")
        self.assertContains(response, "Kein Protokolltext hinterlegt.")

    def test_schedule_rejects_meeting_from_a_different_series(self):
        topic = Topic.objects.create(title="Falsche Zuordnung", series=self.series_a)
        item = AgendaItem.objects.create(meeting=self.meeting, topic=topic)
        self.client.post(
            reverse("meeting", args=[self.meeting.pk]),
            {
                "schedule_item": str(item.pk),
                "target_series": str(self.series_a.pk),
                "target_meeting": str(self.target_meeting.pk),
            },
        )
        topic.refresh_from_db()
        self.assertEqual(topic.series, self.series_a)
        self.assertIsNone(topic.due_date)
        self.assertFalse(TopicTransferHistory.objects.filter(topic=topic).exists())

    def test_history_lists_meetings_series_dates_and_text(self):
        topic = Topic.objects.create(title="Historienthema", series=self.series_a)
        AgendaItem.objects.create(meeting=self.meeting, topic=topic, working_text="Erster Beratungsstand")
        previous = Meeting.objects.create(series=self.series_a, date="2026-11-01")
        AgendaItem.objects.create(meeting=previous, topic=topic, working_text="Vorheriger Beratungsstand")
        page = self.client.get(reverse("meeting", args=[self.meeting.pk]))
        self.assertContains(page, "Historie")
        response = self.client.get(reverse("agenda_topic_history", args=[self.meeting.pk, topic.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Gremium A")
        self.assertContains(response, "01.12.2026")
        self.assertContains(response, "01.11.2026")
        self.assertContains(response, "Erster Beratungsstand")
        self.assertContains(response, "Vorheriger Beratungsstand")


class OpenTopicsViewTests(TestCase):
    def setUp(self):
        from datetime import date
        self.user = User.objects.create_user(username="open-topics-member", password="strong-test-password")
        self.series = MeetingSeries.objects.create(name="Offene-Punkte-Reihe")
        self.other_series = MeetingSeries.objects.create(name="Andere Reihe")
        SeriesAccess.objects.create(user=self.user, series=self.series, role=SeriesAccess.ROLE_PARTICIPANT)
        self.future_meeting = Meeting.objects.create(series=self.series, date=date(2027, 1, 15))
        self.client.force_login(self.user)

    def test_lists_non_done_topics_but_excludes_topics_already_on_future_agenda(self):
        Topic.objects.create(title="Noch offen", series=self.series, status="open")
        Topic.objects.create(title="In Arbeit", series=self.series, status="in_progress")
        Topic.objects.create(title="Erledigt", series=self.series, status="done")
        already_scheduled = Topic.objects.create(title="Schon terminiert", series=self.series, status="open")
        AgendaItem.objects.create(meeting=self.future_meeting, topic=already_scheduled)
        Topic.objects.create(title="Fremde Reihe", series=self.other_series, status="open")

        response = self.client.get(reverse("open_topics"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Noch offen")
        self.assertContains(response, "In Arbeit")
        self.assertNotContains(response, "Erledigt")
        self.assertNotContains(response, "Schon terminiert")
        self.assertNotContains(response, "Fremde Reihe")

    def test_participant_can_schedule_open_topic_on_future_meeting_with_blank_text(self):
        topic = Topic.objects.create(title="Auf Tagesordnung", series=self.series, status="open")
        response = self.client.post(reverse("open_topics"), {
            "schedule_topic": topic.pk,
            "target_meeting": self.future_meeting.pk,
        })
        self.assertRedirects(response, reverse("open_topics"))
        item = AgendaItem.objects.get(meeting=self.future_meeting, topic=topic)
        self.assertEqual(item.working_text, "")
        topic.refresh_from_db()
        self.assertEqual(topic.due_date, self.future_meeting.date)

    def test_reader_cannot_access_open_topics_and_does_not_see_menu_item(self):
        reader = User.objects.create_user(username="open-topics-reader", password="strong-test-password")
        SeriesAccess.objects.create(user=reader, series=self.series, role=SeriesAccess.ROLE_READER)
        self.client.force_login(reader)
        response = self.client.get(reverse("open_topics"))
        self.assertEqual(response.status_code, 403)
        dashboard = self.client.get(reverse("dashboard"))
        self.assertNotContains(dashboard, "Offene Punkte")

    def test_participant_sees_open_topics_but_not_global_change_history(self):
        response = self.client.get(reverse("dashboard"))
        self.assertContains(response, "Offene Punkte")
        self.assertNotContains(response, "Änderungsverlauf")
        history = self.client.get(reverse("audit_history"))
        self.assertEqual(history.status_code, 200)
        self.assertContains(history, "Änderungsverlauf")
        self.assertContains(history, "Für deinen Zugang sind keine Einträge")
        self.assertNotContains(history, "Testeintrag")

    def test_mobile_navigation_keeps_menu_labels_visible(self):
        response = self.client.get(reverse("dashboard"))
        self.assertContains(response, "@media(min-width:1050px)")
        self.assertContains(response, ".sidebar:not(.is-expanded) .nav-links a{font-size:inherit")
        self.assertContains(response, "desktop-menu-toggle")

    def test_moderator_sees_both_menu_items_and_can_open_history(self):
        SeriesAccess.objects.filter(user=self.user, series=self.series).update(role=SeriesAccess.ROLE_MODERATOR)
        dashboard = self.client.get(reverse("dashboard"))
        self.assertContains(dashboard, "Offene Punkte")
        self.assertContains(dashboard, "Änderungsverlauf")
        self.assertEqual(self.client.get(reverse("audit_history")).status_code, 200)

    def test_no_future_meeting_shows_notice_without_creating_meeting(self):
        self.future_meeting.delete()
        Topic.objects.create(title="Ohne Termin", series=self.series, status="open")
        response = self.client.get(reverse("open_topics"))
        self.assertContains(response, "Kein zukünftiger Besprechungstermin")
        self.assertEqual(Meeting.objects.filter(series=self.series).count(), 0)

