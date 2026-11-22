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

    def test_transfer_moves_future_agenda_items_and_keeps_point_responsibility(self):
        from datetime import date
        source_meeting = Meeting.objects.create(series=self.series_a, date=date(2026, 12, 3))
        target_meeting = Meeting.objects.create(series=self.series_b, date=date(2026, 12, 10))
        item = AgendaItem.objects.create(
            meeting=source_meeting, topic=self.topic, working_text="Noch zu beraten",
            assigned_to=self.user,
        )

        response = self.client.post(reverse("topic_transfer", args=[self.topic.pk]), {
            "series": self.series_b.pk, "note": "Gremienwechsel",
        })

        self.assertRedirects(response, reverse("topic_edit", args=[self.topic.pk]))
        item.refresh_from_db()
        self.assertEqual(item.meeting, target_meeting)
        self.assertEqual(item.working_text, "Noch zu beraten")
        self.assertEqual(item.assigned_to, self.user)
        self.assertFalse(AgendaItem.objects.filter(meeting=source_meeting, topic=self.topic).exists())

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
        })
        self.assertRedirects(response, reverse("topic_edit", args=[self.topic.pk]))
        from .models import AuditEvent
        event = AuditEvent.objects.get(topic=self.topic, action="updated")
        self.assertEqual(event.actor, self.user)
        self.assertEqual(event.changes["Titel"]["vorher"], "Audit-Thema")
        self.assertEqual(event.changes["Titel"]["nachher"], "Neuer Titel")
        self.assertNotIn("Beschreibung", event.changes)

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

    def test_agenda_item_can_be_assigned_and_assignment_is_audited(self):
        self.client.force_login(self.member)
        meeting = Meeting.objects.create(series=self.series, date="2026-12-01")
        item = AgendaItem.objects.create(meeting=meeting, topic=self.topic)
        response = self.client.post(
            reverse("topic_agenda_edit", args=[self.topic.pk, item.pk]),
            {"working_text": "", "assigned_to": self.owner.pk},
        )
        self.assertRedirects(response, reverse("topic_edit", args=[self.topic.pk]))
        item.refresh_from_db()
        self.topic.refresh_from_db()
        self.assertEqual(item.assigned_to, self.owner)
        self.assertIsNone(self.topic.assigned_to)
        from .models import AuditEvent
        event = AuditEvent.objects.get(topic=self.topic, action="agenda_edited")
        self.assertEqual(event.changes["Zuständigkeit"]["vorher"], None)
        self.assertEqual(event.changes["Zuständigkeit"]["nachher"], str(self.owner.pk))

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
        self.overdue = Topic.objects.create(title="Überfällige Aufgabe", series=self.series)
        self.due_today = Topic.objects.create(title="Heute terminiert", series=self.series)
        self.point_assigned = Topic.objects.create(title="Punktaufgabe", series=self.series)
        overdue_meeting = Meeting.objects.create(series=self.series, date=today - timedelta(days=2))
        today_meeting = Meeting.objects.create(series=self.series, date=today)
        point_meeting = Meeting.objects.create(series=self.series, date=today + timedelta(days=2))
        AgendaItem.objects.create(meeting=overdue_meeting, topic=self.overdue, assigned_to=self.user)
        AgendaItem.objects.create(meeting=today_meeting, topic=self.due_today, assigned_to=self.user)
        AgendaItem.objects.create(meeting=point_meeting, topic=self.point_assigned, assigned_to=self.user)
        other_topic = Topic.objects.create(title="Aufgabe anderer Person", series=self.series)
        other_meeting = Meeting.objects.create(series=self.series, date=today + timedelta(days=3))
        AgendaItem.objects.create(meeting=other_meeting, topic=other_topic, assigned_to=self.other_user)
        unassigned = Topic.objects.create(title="Nicht zugewiesen", series=self.series)
        AgendaItem.objects.create(meeting=other_meeting, topic=unassigned)
        done_topic = Topic.objects.create(title="Erledigter Tagesordnungspunkt", series=self.series)
        AgendaItem.objects.create(meeting=other_meeting, topic=done_topic, assigned_to=self.user, status="done")
        self.client.force_login(self.user)

    def test_my_tasks_shows_only_my_open_agenda_items_and_overdue_summary(self):
        response = self.client.get(reverse("my_tasks"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context["topics"]), [self.overdue, self.due_today, self.point_assigned])
        self.assertEqual(response.context["overdue_count"], 1)
        self.assertEqual(response.context["due_today_count"], 1)
        self.assertEqual(response.context["without_meeting_count"], 0)
        self.assertContains(response, "Überfällig")
        self.assertContains(response, "Heute auf der Tagesordnung")
        self.assertContains(response, "Punktaufgabe")
        self.assertNotContains(response, "Aufgabe anderer Person")
        self.assertNotContains(response, "Nicht zugewiesen")
        self.assertNotContains(response, "Erledigter Tagesordnungspunkt")

    def test_my_tasks_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse("my_tasks"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)


class OpenTopicsViewTests(TestCase):
    def setUp(self):
        from datetime import date
        self.user = User.objects.create_user(username="open-topics-member", password="strong-test-password")
        self.series = MeetingSeries.objects.create(name="Offene-Punkte-Reihe")
        self.other_series = MeetingSeries.objects.create(name="Andere Reihe")
        SeriesAccess.objects.create(user=self.user, series=self.series, role=SeriesAccess.ROLE_PARTICIPANT)
        self.past_meeting = Meeting.objects.create(series=self.series, date=date(2026, 11, 10))
        self.future_meeting = Meeting.objects.create(series=self.series, date=date(2027, 1, 15))
        self.client.force_login(self.user)

    def test_lists_latest_unfinished_agenda_entries_but_excludes_future_appointments(self):
        open_topic = Topic.objects.create(title="Noch offen", series=self.series)
        in_progress_topic = Topic.objects.create(title="In Arbeit", series=self.series)
        done_topic = Topic.objects.create(title="Erledigt", series=self.series)
        scheduled_topic = Topic.objects.create(title="Schon terminiert", series=self.series)
        AgendaItem.objects.create(meeting=self.past_meeting, topic=open_topic, status="open")
        AgendaItem.objects.create(meeting=self.past_meeting, topic=in_progress_topic, status="in_progress")
        AgendaItem.objects.create(meeting=self.past_meeting, topic=done_topic, status="done")
        AgendaItem.objects.create(meeting=self.past_meeting, topic=scheduled_topic, status="open")
        AgendaItem.objects.create(meeting=self.future_meeting, topic=scheduled_topic, status="open")
        foreign_meeting = Meeting.objects.create(series=self.other_series, date="2026-11-10")
        foreign_topic = Topic.objects.create(title="Fremde Reihe", series=self.other_series)
        AgendaItem.objects.create(meeting=foreign_meeting, topic=foreign_topic, status="open")

        response = self.client.get(reverse("open_topics"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Noch offen")
        self.assertContains(response, "In Arbeit")
        self.assertNotContains(response, "Erledigt")
        self.assertNotContains(response, "Schon terminiert")
        self.assertNotContains(response, "Fremde Reihe")

    def test_participant_can_schedule_open_agenda_item_on_future_meeting(self):
        topic = Topic.objects.create(title="Auf Tagesordnung", series=self.series)
        item = AgendaItem.objects.create(
            meeting=self.past_meeting, topic=topic, working_text="Weiter beraten", status="in_progress"
        )
        response = self.client.post(reverse("open_topics"), {
            "schedule_item": item.pk,
            "target_meeting": self.future_meeting.pk,
        })
        self.assertRedirects(response, reverse("open_topics"))
        new_item = AgendaItem.objects.get(meeting=self.future_meeting, topic=topic)
        self.assertEqual(new_item.working_text, "Weiter beraten")
        self.assertEqual(new_item.status, "in_progress")

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

class TopicAgendaCsvImportTests(TestCase):
    def setUp(self):
        from django.contrib.auth.models import Group
        self.admin = User.objects.create_superuser(
            username="csv-admin", email="csv-admin@example.com", password="strong-test-password"
        )
        self.series = MeetingSeries.objects.create(name="CSV-Reihe")
        self.client.force_login(self.admin)

    def _csv(self, rows):
        import csv
        from io import StringIO
        output = StringIO()
        writer = csv.writer(output, delimiter=";")
        writer.writerow([
            "series", "meeting_date", "meeting_title", "topic_key", "topic_id",
            "topic_title", "topic_description", "topic_due_date", "topic_status",
            "responsible_username", "agenda_text", "position", "carried_forward",
        ])
        for row in rows:
            if len(row) == 8:
                row = [*row[:7], "", *row[7:]]
            writer.writerow(["CSV-Reihe", *row])
        return output.getvalue()

    def test_csv_export_keeps_meeting_and_topic_series_separate(self):
        import csv
        from io import StringIO

        topic_series = MeetingSeries.objects.create(name="Themenreihe")
        topic = Topic.objects.create(title="Reihenübergreifendes Thema", series=topic_series)
        meeting = Meeting.objects.create(series=self.series, date="2026-12-03", title="Sondersitzung")
        AgendaItem.objects.create(meeting=meeting, topic=topic)

        response = self.client.get(reverse("admin:meetings_topic_csv_export"))
        self.assertEqual(response.status_code, 200)
        rows = list(csv.DictReader(StringIO(response.content.decode("utf-8-sig")), delimiter=";"))
        exported = next(row for row in rows if row.get("topic_title") == "Reihenübergreifendes Thema")
        self.assertEqual(exported["series"], "CSV-Reihe")
        self.assertEqual(exported["topic_series"], "Themenreihe")

    def test_admin_can_download_sample_and_open_import(self):
        sample = self.client.get(reverse("admin:meetings_topic_csv_sample"))
        self.assertEqual(sample.status_code, 200)
        self.assertIn("muster_themen_und_punkte.csv", sample["Content-Disposition"])
        page = self.client.get(reverse("admin:meetings_topic_csv_import"))
        self.assertEqual(page.status_code, 200)
        self.assertContains(page, "Muster-CSV herunterladen")

    def test_import_creates_topic_meeting_and_agenda_item(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        text = self._csv([[
            "2026-12-03", "Reguläre Sitzung", "CSV-1", "", "Neues Thema",
            "Beschreibung", "2026-12-03", "open", "", "Beratungstext", "1", "false",
        ]])
        upload = SimpleUploadedFile("import.csv", text.encode("utf-8"), content_type="text/csv")
        response = self.client.post(reverse("admin:meetings_topic_csv_import"), {"csv_file": upload})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Importvorschau")
        token = response.context["preview"]["token"]
        response = self.client.post(reverse("admin:meetings_topic_csv_import"), {
            "action": "confirm", "token": token,
        })
        self.assertRedirects(response, reverse("admin:meetings_topic_changelist"))
        topic = Topic.objects.get(title="Neues Thema")
        meeting = Meeting.objects.get(series=self.series, date="2026-12-03")
        item = AgendaItem.objects.get(meeting=meeting, topic=topic)
        self.assertEqual(item.working_text, "Beratungstext")
        self.assertEqual(item.position, 1)

    def test_repeated_topic_key_creates_one_topic_and_multiple_agenda_items(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        text = self._csv([
            ["2026-12-03", "", "CSV-1", "", "Mehrfachthema", "Beschreibung", "", "open", "", "Erster Stand", "1", "false"],
            ["2027-01-14", "", "CSV-1", "", "Mehrfachthema", "Beschreibung", "", "open", "", "Zweiter Stand", "1", "true"],
        ])
        upload = SimpleUploadedFile("import.csv", text.encode("utf-8"), content_type="text/csv")
        response = self.client.post(reverse("admin:meetings_topic_csv_import"), {"csv_file": upload})
        self.assertEqual(response.status_code, 200)
        token = response.context["preview"]["token"]
        self.client.post(reverse("admin:meetings_topic_csv_import"), {"action": "confirm", "token": token})
        topic = Topic.objects.get(title="Mehrfachthema")
        self.assertEqual(AgendaItem.objects.filter(topic=topic).count(), 2)
        self.assertEqual(Meeting.objects.filter(series=self.series).count(), 2)


class TopicAgendaCsvImportTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username="csv-admin", email="csv-admin@example.com", password="strong-test-password"
        )
        self.series = MeetingSeries.objects.create(name="CSV-Reihe")
        self.client.force_login(self.admin)

    def _csv(self, rows, topic_series_name="CSV-Reihe"):
        import csv
        from io import StringIO
        output = StringIO()
        writer = csv.writer(output, delimiter=";")
        writer.writerow([
            "series", "topic_series", "meeting_date", "meeting_title", "topic_title",
            "topic_current_status", "topic_due_date", "topic_status",
            "responsible_username", "responsible_kurzbezeichnung",
            "agenda_responsible_username", "agenda_responsible_kurzbezeichnung", "agenda_text",
        ])
        for row in rows:
            if len(row) == 8:
                row = [*row[:7], "", "", "", row[7]]
            elif len(row) == 9:
                row = [*row[:8], "", "", row[8]]
            elif len(row) == 10:
                row = [*row[:4], "", *row[4:]]
            writer.writerow(["CSV-Reihe", topic_series_name, *row])
        return output.getvalue()

    def _confirm_import(self, text):
        from django.core.files.uploadedfile import SimpleUploadedFile
        upload = SimpleUploadedFile("import.csv", text.encode("utf-8"), content_type="text/csv")
        response = self.client.post(reverse("admin:meetings_topic_csv_import"), {"csv_file": upload})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Importvorschau")
        token = response.context["preview"]["token"]
        return self.client.post(reverse("admin:meetings_topic_csv_import"), {
            "action": "confirm", "token": token,
        })

    def test_admin_can_download_sample_and_open_import(self):
        sample = self.client.get(reverse("admin:meetings_topic_csv_sample"))
        self.assertEqual(sample.status_code, 200)
        self.assertIn("muster_themen_und_punkte.csv", sample["Content-Disposition"])
        self.assertNotContains(sample, "topic_key")
        sample_header = sample.content.decode("utf-8-sig").splitlines()[0]
        self.assertNotIn("topic_due_date", sample_header)
        self.assertContains(sample, "agenda_responsible_username")
        page = self.client.get(reverse("admin:meetings_topic_csv_import"))
        self.assertEqual(page.status_code, 200)
        self.assertContains(page, "Muster-CSV herunterladen")

    def test_import_creates_topic_meeting_and_agenda_item(self):
        response = self._confirm_import(self._csv([[
            "2026-12-03", "Reguläre Sitzung", "Neues Thema",
            "Aktueller Stand", "2026-12-03", "open", "", "Beratungstext",
        ]]))
        self.assertRedirects(response, reverse("admin:meetings_topic_changelist"))
        topic = Topic.objects.get(title="Neues Thema")
        meeting = Meeting.objects.get(series=self.series, date="2026-12-03")
        item = AgendaItem.objects.get(meeting=meeting, topic=topic)
        self.assertEqual(topic.description, "")
        self.assertEqual(item.working_text, "Aktueller Stand\nBeratungstext")
        self.assertEqual(item.position, 0)
        self.assertFalse(item.carried_forward)

    def test_repeated_topic_title_is_matched_automatically_and_missing_meetings_created(self):
        response = self._confirm_import(self._csv([
            ["2026-12-03", "", "Mehrfachthema", "Sachstand", "", "open", "", "Erster Stand"],
            ["2027-01-14", "", "Mehrfachthema", "Sachstand", "", "open", "", "Zweiter Stand"],
        ]))
        self.assertRedirects(response, reverse("admin:meetings_topic_changelist"))
        topic = Topic.objects.get(title="Mehrfachthema")
        self.assertEqual(AgendaItem.objects.filter(topic=topic).count(), 2)
        self.assertEqual(Meeting.objects.filter(series=self.series).count(), 2)
        later_item = AgendaItem.objects.get(topic=topic, meeting__date="2027-01-14")
        self.assertTrue(later_item.carried_forward)

    def test_responsible_user_can_be_resolved_by_short_description_without_username(self):
        from .models import UserProfile
        responsible = User.objects.create_user(
            username="short-name-user", password="strong-test-password"
        )
        UserProfile.objects.create(user=responsible, short_description="Teamleitung Bau")
        self._confirm_import(self._csv([[
            "2026-12-03", "", "Verantwortliches Thema", "", "", "open", "",
            "Teamleitung Bau", "Sachstand",
        ]]))
        topic = Topic.objects.get(title="Verantwortliches Thema")
        item = AgendaItem.objects.get(topic=topic)
        self.assertIsNone(topic.assigned_to)
        self.assertEqual(item.assigned_to, responsible)

    def test_agenda_responsible_user_is_imported_independently_from_topic_owner(self):
        item_owner = User.objects.create_user(username="agenda-csv-owner", password="strong-test-password")
        response = self._confirm_import(self._csv([[
            "2026-12-03", "", "Punktverantwortung", "Sachstand", "open",
            "", "", "agenda-csv-owner", "", "Punkttext",
        ]]))
        self.assertRedirects(response, reverse("admin:meetings_topic_changelist"))
        topic = Topic.objects.get(title="Punktverantwortung")
        item = AgendaItem.objects.get(topic=topic)
        self.assertIsNone(topic.assigned_to)
        self.assertEqual(item.assigned_to, item_owner)
        self.assertEqual(item.working_text, "Punkttext")

    def test_csv_preserves_topic_series_separately_from_meeting_series(self):
        topic_series = MeetingSeries.objects.create(name="Themenreihe")
        response = self._confirm_import(self._csv([[
            "2026-12-03", "Sondersitzung", "Thema aus anderer Reihe",
            "Sachstand", "", "open", "", "Punkttext",
        ]], topic_series_name="Themenreihe"))
        self.assertRedirects(response, reverse("admin:meetings_topic_changelist"))
        topic = Topic.objects.get(title="Thema aus anderer Reihe")
        item = AgendaItem.objects.get(topic=topic)
        self.assertEqual(topic.series, topic_series)
        self.assertEqual(item.meeting.series, self.series)
        self.assertEqual(item.working_text, "Punkttext")

    def test_legacy_csv_without_topic_series_defaults_to_meeting_series(self):
        import csv
        from io import StringIO

        output = StringIO()
        writer = csv.writer(output, delimiter=";")
        writer.writerow([
            "series", "meeting_date", "meeting_title", "topic_title",
            "topic_current_status", "topic_due_date", "topic_status",
            "responsible_username", "responsible_kurzbezeichnung", "agenda_text",
        ])
        writer.writerow(["CSV-Reihe", "2026-12-03", "Sitzung", "Altes CSV-Thema", "Sachstand", "", "open", "", "", "Punkttext"])
        self._confirm_import(output.getvalue())
        topic = Topic.objects.get(title="Altes CSV-Thema")
        item = AgendaItem.objects.get(topic=topic)
        self.assertEqual(topic.series, self.series)
        self.assertEqual(item.meeting.series, self.series)

    def test_legacy_due_date_becomes_a_separate_agenda_item(self):
        response = self._confirm_import(self._csv([[
            "2026-12-03", "Reguläre Sitzung", "Alte Wiedervorlage",
            "Sachstand", "2027-01-14", "open", "", "Erster Stand",
        ]]))
        self.assertRedirects(response, reverse("admin:meetings_topic_changelist"))
        topic = Topic.objects.get(title="Alte Wiedervorlage")
        self.assertEqual(
            list(AgendaItem.objects.filter(topic=topic).values_list("meeting__date", flat=True).order_by("meeting__date")),
            [__import__("datetime").date(2026, 12, 3), __import__("datetime").date(2027, 1, 14)],
        )

    def test_explicit_future_csv_row_wins_over_legacy_synthetic_followup(self):
        self._confirm_import(self._csv([
            ["2026-12-03", "Reguläre Sitzung", "Legacy-Doppelzeile", "Sachstand", "2027-01-14", "open", "", "Text Dezember"],
            ["2027-01-14", "Reguläre Sitzung", "Legacy-Doppelzeile", "Sachstand", "2027-01-14", "open", "", "Expliziter Text Januar"],
        ]))
        topic = Topic.objects.get(title="Legacy-Doppelzeile")
        future_item = AgendaItem.objects.get(topic=topic, meeting__date="2027-01-14")
        self.assertEqual(future_item.working_text, "Expliziter Text Januar")
        self.assertEqual(AgendaItem.objects.filter(topic=topic).count(), 2)

    def test_unknown_or_ambiguous_short_description_is_rejected(self):
        from .models import UserProfile
        first = User.objects.create_user(username="short-one", password="strong-test-password")
        second = User.objects.create_user(username="short-two", password="strong-test-password")
        UserProfile.objects.create(user=first, short_description="Doppelt")
        UserProfile.objects.create(user=second, short_description="Doppelt")
        from .topic_csv import parse_topic_agenda_csv
        text = self._csv([[
            "2026-12-03", "", "Mehrdeutiges Thema", "", "", "open", "",
            "Doppelt", "Text",
        ]])
        rows, errors = parse_topic_agenda_csv(text)
        self.assertEqual(rows, [])
        self.assertTrue(any("nicht eindeutig" in error for error in errors))

    def test_position_follows_csv_row_order_for_each_meeting(self):
        self._confirm_import(self._csv([
            ["2026-12-03", "", "Erstes Thema", "", "", "open", "", "Text 1"],
            ["2026-12-03", "", "Zweites Thema", "", "", "open", "", "Text 2"],
        ]))
        meeting = Meeting.objects.get(series=self.series, date="2026-12-03")
        self.assertEqual(
            list(meeting.agenda_items.order_by("position").values_list("topic__title", flat=True)),
            ["Erstes Thema", "Zweites Thema"],
        )


class OrganizationBrandColorTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(username="brand-admin", email="brand-admin@example.com", password="strong-test-password")
        self.client.force_login(self.admin)

    def test_brand_color_defaults_and_mode_overrides(self):
        from .models import OrganizationSettings
        settings = OrganizationSettings.objects.create(name="Test")
        self.assertEqual(OrganizationSettings.current_brand_colors(), {
            "primary_color": "#00549F", "primary_color_light": "#00549F", "primary_color_dark": "#00549F",
            "secondary_color": "#8FC5FF", "secondary_color_light": "#8FC5FF", "secondary_color_dark": "#8FC5FF",
            "tertiary_color": "#FFCC00", "tertiary_color_light": "#FFCC00", "tertiary_color_dark": "#FFCC00",
        })
        settings.primary_color = "#123456"
        settings.primary_color_light = "#ABCDEF"
        settings.secondary_color_dark = "#234567"
        settings.tertiary_color = "#FEDCBA"
        settings.save()
        colors = OrganizationSettings.current_brand_colors()
        self.assertEqual(colors["primary_color_light"], "#ABCDEF")
        self.assertEqual(colors["primary_color_dark"], "#123456")
        self.assertEqual(colors["secondary_color_light"], "#8FC5FF")
        self.assertEqual(colors["secondary_color_dark"], "#234567")
        self.assertEqual(colors["tertiary_color_light"], "#FEDCBA")

    def test_all_base_and_optional_mode_colors_validate_hex_values(self):
        from django.core.exceptions import ValidationError
        from .models import OrganizationSettings
        settings = OrganizationSettings()
        for field in ("primary_color", "secondary_color", "tertiary_color"):
            setattr(settings, field, "blue")
            with self.subTest(field=field), self.assertRaises(ValidationError):
                settings.full_clean()
            setattr(settings, field, "#123456")
        for field in ("primary_color_light", "primary_color_dark", "secondary_color_light", "secondary_color_dark", "tertiary_color_light", "tertiary_color_dark"):
            setattr(settings, field, "123456")
            with self.subTest(field=field), self.assertRaises(ValidationError):
                settings.full_clean()
            setattr(settings, field, "")
        settings.full_clean()

    def test_admin_can_edit_all_colors_and_templates_receive_mode_palette(self):
        from .models import OrganizationSettings
        settings = OrganizationSettings.objects.create(name="Test")
        response = self.client.get(reverse("admin:meetings_organizationsettings_change", args=[settings.pk]))
        self.assertEqual(response.status_code, 200)
        for label in ("Primärfarbe", "Sekundärfarbe", "Tertiärfarbe"):
            self.assertContains(response, label)
        response = self.client.post(reverse("admin:meetings_organizationsettings_change", args=[settings.pk]), {
            "name": "Test", "short_name": "MM",
            "primary_color": "#123456", "primary_color_light": "#ABCDEF", "primary_color_dark": "",
            "secondary_color": "#234567", "secondary_color_light": "", "secondary_color_dark": "#345678",
            "tertiary_color": "#456789", "tertiary_color_light": "#56789A", "tertiary_color_dark": "",
            "_save": "Speichern",
        })
        self.assertEqual(response.status_code, 302)
        settings.refresh_from_db()
        self.assertEqual(settings.primary_color, "#123456")
        self.assertEqual(settings.secondary_color_dark, "#345678")
        self.assertEqual(settings.tertiary_color_light, "#56789A")
        page = self.client.get(reverse("dashboard"))
        self.assertEqual(page.status_code, 200)
        self.assertContains(page, "--primary-color: #ABCDEF")
        self.assertContains(page, "--secondary-color: #234567")
        self.assertContains(page, "--tertiary-color: #56789A")
        page = self.client.get(reverse("admin:index"))
        self.assertEqual(page.status_code, 200)
        self.assertContains(page, "--primary-color: #ABCDEF")
        self.assertContains(page, "--secondary-color: #234567")
        self.assertContains(page, "--tertiary-color: #56789A")
