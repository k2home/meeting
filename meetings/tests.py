from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from .models import Meeting, MeetingSeries, Topic, TopicTransferHistory, AgendaItem

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
        self.client.force_login(self.user)
        response = self.client.get(reverse("audit_history"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Testeintrag")


class TopicTaskManagementTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="owner", password="strong-test-password")
        self.member = User.objects.create_user(username="member", password="strong-test-password")
        self.series = MeetingSeries.objects.create(name="Aufgaben-Reihe")
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


class ProtocolExportTests(TestCase):
    def setUp(self):
        from .models import TopicSnapshot

        self.user = User.objects.create_user(username="protocol-user", password="strong-test-password")
        self.client.force_login(self.user)
        self.series = MeetingSeries.objects.create(name="Team & Betrieb")
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

    def test_series_delete_is_blocked_while_meetings_exist(self):
        response = self.client.post(reverse("series_delete", args=[self.series.pk]))
        self.assertRedirects(response, reverse("series_admin"))
        self.assertTrue(MeetingSeries.objects.filter(pk=self.series.pk).exists())

    def test_finalized_meeting_cannot_be_moved_or_deleted(self):
        from django.utils import timezone

        self.meeting.finalized_at = timezone.now()
        self.meeting.save(update_fields=["finalized_at"])
        response = self.client.post(
            reverse("meeting_edit", args=[self.meeting.pk]),
            {"date": (self.today + timezone.timedelta(days=30)).isoformat()},
        )
        self.assertRedirects(response, reverse("meeting", args=[self.meeting.pk]))
        self.client.post(reverse("meeting_delete", args=[self.meeting.pk]))
        self.assertTrue(Meeting.objects.filter(pk=self.meeting.pk).exists())

