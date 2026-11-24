from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from .models import Meeting, MeetingSeries, SeriesAccess, Topic, TopicTransferHistory, AgendaItem

User = get_user_model()

class AccountSecurityTests(TestCase):
    def test_password_policy_accepts_eight_characters_with_required_character_types(self):
        from django.contrib.auth.password_validation import validate_password

        validate_password("Abcdef1!")

    def test_password_policy_rejects_missing_character_types(self):
        from django.contrib.auth.password_validation import validate_password
        from django.core.exceptions import ValidationError

        for password in ("abcdefgh", "ABCDEFGH", "Abcdefg1"):
            with self.subTest(password=password):
                with self.assertRaises(ValidationError):
                    validate_password(password)

    def test_password_policy_rejects_passwords_shorter_than_eight_characters(self):
        from django.contrib.auth.password_validation import validate_password
        from django.core.exceptions import ValidationError

        with self.assertRaises(ValidationError):
            validate_password("Abc1!")

    def test_unknown_username_does_not_create_account(self):
        User.objects.create_user(username="existing-member", password="strong-test-password")
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
        # The shared confirmation-dialog script contains escaped newlines;
        # the rendered audit entry itself is verified above with HTML line breaks.


    def test_deleted_series_event_is_not_visible_to_former_series_moderator(self):
        from .models import AuditEvent

        SeriesAccess.objects.filter(user=self.user, series=self.series).update(
            role=SeriesAccess.ROLE_MODERATOR
        )
        self.client.force_login(self.user)
        response = self.client.post(reverse("series_delete", args=[self.series.pk]))
        self.assertRedirects(response, reverse("dashboard"))

        event = AuditEvent.objects.get(action="deleted", summary__contains="Audit-Reihe")
        self.assertIsNone(event.series_id)
        response = self.client.get(reverse("audit_history"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Audit-Reihe gelöscht")

        admin = User.objects.create_superuser(
            username="audit-admin", email="audit-admin@example.com", password="strong-test-password"
        )
        self.client.force_login(admin)
        response = self.client.get(reverse("audit_history"))
        self.assertContains(response, "Audit-Reihe“ gelöscht")

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

    def test_my_tasks_separates_main_ownership_from_future_agenda_assignments(self):
        response = self.client.get(reverse("my_tasks"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context["main_topics"]), [])
        self.assertEqual([item.topic for item in response.context["agenda_tasks"]], [self.due_today, self.point_assigned])
        self.assertContains(response, "Hauptzuständigkeit")
        self.assertContains(response, "Eigene Zuständigkeiten bei zukünftigen Terminen")
        self.assertContains(response, "Punktaufgabe")
        self.assertNotContains(response, "Aufgabe anderer Person")
        self.assertNotContains(response, "Nicht zugewiesen")
        self.assertNotContains(response, "Erledigter Tagesordnungspunkt")

    def test_my_tasks_lists_topic_owner_separately(self):
        self.overdue.assigned_to = self.user
        self.overdue.save(update_fields=["assigned_to"])
        response = self.client.get(reverse("my_tasks"))
        self.assertEqual(list(response.context["main_topics"]), [self.overdue])
        self.assertNotIn(self.overdue, [item.topic for item in response.context["agenda_tasks"]])

    def test_upcoming_meeting_prevents_previous_agenda_item_from_appearing_overdue(self):
        from datetime import timedelta
        from django.utils import timezone

        self.overdue.assigned_to = self.user
        self.overdue.save(update_fields=["assigned_to"])
        upcoming_meeting = Meeting.objects.create(
            series=self.series, date=timezone.localdate() + timedelta(days=7)
        )
        AgendaItem.objects.create(
            meeting=upcoming_meeting, topic=self.overdue, status="open"
        )

        response = self.client.get(reverse("my_tasks"))

        self.assertEqual(response.status_code, 200)
        topic = next(
            item for item in response.context["main_topics"]
            if item.pk == self.overdue.pk
        )
        self.assertEqual(topic.next_meeting_date, upcoming_meeting.date)
        self.assertNotContains(response, "Überfällig ·")
        self.assertContains(
            response, upcoming_meeting.date.strftime("%d.%m.%Y")
        )

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

    def test_hides_open_items_from_today_until_meeting_is_finalized(self):
        from django.utils import timezone

        today = timezone.localdate()
        current_topic = Topic.objects.create(title="Heutige Sitzung noch offen", series=self.series)
        finalized_series = MeetingSeries.objects.create(name="Abgeschlossene Tagesreihe")
        SeriesAccess.objects.create(
            user=self.user, series=finalized_series, role=SeriesAccess.ROLE_PARTICIPANT
        )
        finalized_topic = Topic.objects.create(
            title="Heutige Sitzung abgeschlossen", series=finalized_series
        )
        current_meeting = Meeting.objects.create(series=self.series, date=today)
        finalized_meeting = Meeting.objects.create(
            series=finalized_series, date=today, finalized_at=timezone.now()
        )
        AgendaItem.objects.create(meeting=current_meeting, topic=current_topic, status="open")
        AgendaItem.objects.create(meeting=finalized_meeting, topic=finalized_topic, status="open")

        response = self.client.get(reverse("open_topics"))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Heutige Sitzung noch offen")
        self.assertContains(response, "Heutige Sitzung abgeschlossen")

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
        self.assertEqual(new_item.working_text, "")
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

    def test_import_without_optional_columns_preserves_existing_topic_and_agenda_values(self):
        import csv
        from io import StringIO
        topic_owner = User.objects.create_user(username="preserved-topic-owner", password="strong-test-password")
        agenda_owner = User.objects.create_user(username="preserved-agenda-owner", password="strong-test-password")
        topic = Topic.objects.create(
            title="Nur Pflichtspalten", series=self.series, status="archived", assigned_to=topic_owner,
        )
        meeting = Meeting.objects.create(series=self.series, date="2026-12-03")
        item = AgendaItem.objects.create(
            meeting=meeting, topic=topic, working_text="Bestehender Text",
            assigned_to=agenda_owner, status="in_progress",
        )
        output = StringIO()
        writer = csv.writer(output, delimiter=";")
        writer.writerow(["series", "meeting_date", "topic_title"])
        writer.writerow(["CSV-Reihe", "2026-12-03", topic.title])
        response = self._confirm_import(output.getvalue())
        self.assertRedirects(response, reverse("admin:meetings_topic_changelist"))
        topic.refresh_from_db()
        item.refresh_from_db()
        self.assertEqual(topic.status, "archived")
        self.assertEqual(topic.assigned_to, topic_owner)
        self.assertEqual(item.working_text, "Bestehender Text")
        self.assertEqual(item.assigned_to, agenda_owner)
        self.assertEqual(item.status, "in_progress")

    def test_import_rejects_conflicting_topic_fields_across_rows(self):
        from .topic_csv import parse_topic_agenda_csv
        text = self._modern_csv([
            ["2026-12-03", "", "Widerspruch", "open", "open", "m.mustermann", "", "", "", "Text 1"],
            ["2027-01-14", "", "Widerspruch", "done", "open", "a.beispiel", "", "", "", "Text 2"],
        ])
        rows, errors = parse_topic_agenda_csv(text)
        self.assertEqual(rows, [])
        self.assertTrue(any("widersprüchliche Werte" in error for error in errors))

    def test_admin_can_download_sample_and_open_import(self):
        sample = self.client.get(reverse("admin:meetings_topic_csv_sample"))
        self.assertEqual(sample.status_code, 200)
        self.assertIn("muster_themen_und_punkte.csv", sample["Content-Disposition"])
        page = self.client.get(reverse("admin:meetings_topic_csv_import"))
        self.assertEqual(page.status_code, 200)
        self.assertContains(page, "Muster-CSV herunterladen")

    def test_removed_topic_current_status_column_is_rejected(self):
        import csv
        from io import StringIO
        from .topic_csv import parse_topic_agenda_csv

        output = StringIO()
        writer = csv.writer(output, delimiter=";")
        writer.writerow(["series", "meeting_date", "topic_title", "topic_current_status", "agenda_text"])
        writer.writerow(["CSV-Reihe", "2026-12-03", "Altformat", "Alter Text", "Neuer Punkttext"])
        rows, errors = parse_topic_agenda_csv(output.getvalue())
        self.assertEqual(rows, [])
        self.assertTrue(any("Unbekannte CSV-Spalten" in error for error in errors))

    def test_import_separates_topic_and_agenda_status_and_responsibility(self):
        topic_owner = User.objects.create_user(username="csv-topic-owner", password="strong-test-password")
        point_owner = User.objects.create_user(username="csv-point-owner", password="strong-test-password")
        text = self._modern_csv([[
            "2026-12-03", "Sitzung", "Status-Trennung", "archived", "in_progress",
            "csv-topic-owner", "", "csv-point-owner", "", "Punkttext",
        ]])
        response = self._confirm_import(text)
        self.assertRedirects(response, reverse("admin:meetings_topic_changelist"))
        topic = Topic.objects.get(title="Status-Trennung")
        item = AgendaItem.objects.get(topic=topic)
        self.assertEqual(topic.status, "archived")
        self.assertEqual(topic.assigned_to, topic_owner)
        self.assertEqual(item.status, "in_progress")
        self.assertEqual(item.assigned_to, point_owner)
        self.assertEqual(item.working_text, "Punkttext")

    def test_export_and_import_preserve_standalone_topics_and_followup_relations(self):
        import csv
        from io import StringIO
        from .topic_csv import parse_topic_agenda_csv

        topic = Topic.objects.create(title="Wiedervorlage-Rundlauf", series=self.series)
        source_meeting = Meeting.objects.create(series=self.series, date="2026-12-03")
        target_meeting = Meeting.objects.create(series=self.series, date="2027-01-14")
        source_item = AgendaItem.objects.create(meeting=source_meeting, topic=topic, working_text="Ursprung")
        followup_item = AgendaItem.objects.create(
            meeting=target_meeting, topic=topic, working_text="Fortsetzung", followup_of=source_item,
        )
        standalone = Topic.objects.create(title="Thema ohne Tagesordnung", series=self.series)

        response = self.client.get(reverse("admin:meetings_topic_csv_export"))
        self.assertEqual(response.status_code, 200)
        text = response.content.decode("utf-8-sig")
        rows = list(csv.DictReader(StringIO(text), delimiter=";"))
        exported_followup = next(row for row in rows if row["topic_title"] == topic.title and row["meeting_date"] == "2027-01-14")
        exported_standalone = next(row for row in rows if row["topic_title"] == standalone.title)
        self.assertEqual(exported_followup["followup_series"], "CSV-Reihe")
        self.assertEqual(exported_followup["followup_meeting_date"], "2026-12-03")
        self.assertEqual(exported_standalone["record_type"], "topic")
        self.assertEqual(exported_standalone["meeting_date"], "")

        parsed, errors = parse_topic_agenda_csv(text)
        self.assertEqual(errors, [])
        self.assertTrue(any(row.get("record_type") == "topic" for row in parsed))
        self.assertTrue(any(row.get("followup_series_id") for row in parsed))

        result = self._confirm_import(text)
        self.assertRedirects(result, reverse("admin:meetings_topic_changelist"))
        followup_item.refresh_from_db()
        self.assertEqual(followup_item.followup_of_id, source_item.pk)
        self.assertTrue(Topic.objects.filter(pk=standalone.pk).exists())

    def test_topic_csv_export_neutralizes_spreadsheet_formulas(self):
        import csv
        from io import StringIO
        topic = Topic.objects.create(title="=HYPERLINK(1)", series=self.series)
        meeting = Meeting.objects.create(series=self.series, date="2026-12-03")
        AgendaItem.objects.create(meeting=meeting, topic=topic)
        response = self.client.get(reverse("admin:meetings_topic_csv_export"))
        rows = list(csv.DictReader(StringIO(response.content.decode("utf-8-sig")), delimiter=";"))
        exported = next(row for row in rows if row["topic_title"].endswith("HYPERLINK(1)"))
        self.assertTrue(exported["topic_title"].startswith("'="))

    def test_export_contains_topic_and_agenda_fields_independently(self):
        import csv
        from io import StringIO

        topic_owner = User.objects.create_user(username="export-topic-owner", password="strong-test-password")
        point_owner = User.objects.create_user(username="export-point-owner", password="strong-test-password")
        topic = Topic.objects.create(
            title="Export-Trennung", series=self.series, status="archived", assigned_to=topic_owner,
        )
        meeting = Meeting.objects.create(series=self.series, date="2026-12-03", title="Exporttermin")
        AgendaItem.objects.create(
            meeting=meeting, topic=topic, status="in_progress", assigned_to=point_owner,
            working_text="Exportierter Punkttext",
        )
        response = self.client.get(reverse("admin:meetings_topic_csv_export"))
        rows = list(csv.DictReader(StringIO(response.content.decode("utf-8-sig")), delimiter=";"))
        exported = next(row for row in rows if row.get("topic_title") == "Export-Trennung")
        self.assertEqual(exported["topic_status"], "archived")
        self.assertEqual(exported["agenda_status"], "in_progress")
        self.assertEqual(exported["responsible_username"], "export-topic-owner")
        self.assertEqual(exported["agenda_responsible_username"], "export-point-owner")
        self.assertEqual(exported["agenda_text"], "Exportierter Punkttext")

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
            "topic_due_date", "topic_status", "responsible_username",
            "responsible_kurzbezeichnung", "agenda_responsible_username",
            "agenda_responsible_kurzbezeichnung", "agenda_text",
        ])
        for row in rows:
            if len(row) != 10:
                raise AssertionError(f"Expected 10 row values, got {len(row)}: {row!r}")
            writer.writerow(["CSV-Reihe", topic_series_name, *row])
        return output.getvalue()

    def _modern_csv(self, rows):
        import csv
        from io import StringIO
        output = StringIO()
        writer = csv.writer(output, delimiter=";")
        writer.writerow([
            "series", "topic_series", "meeting_date", "meeting_title", "topic_title",
            "topic_status", "agenda_status", "responsible_username",
            "responsible_kurzbezeichnung", "agenda_responsible_username",
            "agenda_responsible_kurzbezeichnung", "agenda_text",
        ])
        for row in rows:
            writer.writerow(["CSV-Reihe", "CSV-Reihe", *row])
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
        self.assertNotIn("topic_current_status", sample_header)
        self.assertContains(sample, "agenda_responsible_username")
        page = self.client.get(reverse("admin:meetings_topic_csv_import"))
        self.assertEqual(page.status_code, 200)
        self.assertContains(page, "Muster-CSV herunterladen")

    def test_import_creates_topic_meeting_and_agenda_item(self):
        response = self._confirm_import(self._csv([[
            "2026-12-03", "Reguläre Sitzung", "Neues Thema",
            "2026-12-03", "open", "", "", "", "", "Beratungstext",
        ]]))
        self.assertRedirects(response, reverse("admin:meetings_topic_changelist"))
        topic = Topic.objects.get(title="Neues Thema")
        meeting = Meeting.objects.get(series=self.series, date="2026-12-03")
        item = AgendaItem.objects.get(meeting=meeting, topic=topic)
        self.assertEqual(item.working_text, "Beratungstext")
        self.assertEqual(item.position, 0)
        self.assertFalse(item.carried_forward)

    def test_repeated_topic_title_is_matched_automatically_and_missing_meetings_created(self):
        response = self._confirm_import(self._csv([
            ["2026-12-03", "", "Mehrfachthema", "", "open", "", "", "", "", "Erster Stand"],
            ["2027-01-14", "", "Mehrfachthema", "", "open", "", "", "", "", "Zweiter Stand"],
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
            "2026-12-03", "", "Verantwortliches Thema", "", "open", "",
            "Teamleitung Bau", "", "", "Sachstand",
        ]]))
        topic = Topic.objects.get(title="Verantwortliches Thema")
        item = AgendaItem.objects.get(topic=topic)
        self.assertEqual(topic.assigned_to, responsible)
        self.assertEqual(item.assigned_to, responsible)

    def test_agenda_responsible_user_is_imported_independently_from_topic_owner(self):
        item_owner = User.objects.create_user(username="agenda-csv-owner", password="strong-test-password")
        response = self._confirm_import(self._csv([[
            "2026-12-03", "", "Punktverantwortung", "", "open",
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
            "", "open", "", "", "", "", "Punkttext",
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
            "topic_due_date", "topic_status",
            "responsible_username", "responsible_kurzbezeichnung", "agenda_text",
        ])
        writer.writerow(["CSV-Reihe", "2026-12-03", "Sitzung", "Altes CSV-Thema", "", "open", "", "", "Punkttext"])
        self._confirm_import(output.getvalue())
        topic = Topic.objects.get(title="Altes CSV-Thema")
        item = AgendaItem.objects.get(topic=topic)
        self.assertEqual(topic.series, self.series)
        self.assertEqual(item.meeting.series, self.series)

    def test_legacy_due_date_becomes_a_separate_agenda_item(self):
        response = self._confirm_import(self._csv([[
            "2026-12-03", "Reguläre Sitzung", "Alte Wiedervorlage",
            "2027-01-14", "open", "", "", "", "", "Erster Stand",
        ]]))
        self.assertRedirects(response, reverse("admin:meetings_topic_changelist"))
        topic = Topic.objects.get(title="Alte Wiedervorlage")
        self.assertEqual(
            list(AgendaItem.objects.filter(topic=topic).values_list("meeting__date", flat=True).order_by("meeting__date")),
            [__import__("datetime").date(2026, 12, 3), __import__("datetime").date(2027, 1, 14)],
        )

    def test_explicit_future_csv_row_wins_over_legacy_synthetic_followup(self):
        self._confirm_import(self._csv([
            ["2026-12-03", "Reguläre Sitzung", "Legacy-Doppelzeile", "2027-01-14", "open", "", "", "", "", "Text Dezember"],
            ["2027-01-14", "Reguläre Sitzung", "Legacy-Doppelzeile", "2027-01-14", "open", "", "", "", "", "Expliziter Text Januar"],
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
            "2026-12-03", "", "Mehrdeutiges Thema", "", "open", "",
            "Doppelt", "", "", "Text",
        ]])
        rows, errors = parse_topic_agenda_csv(text)
        self.assertEqual(rows, [])
        self.assertTrue(any("nicht eindeutig" in error for error in errors))

    def test_position_follows_csv_row_order_for_each_meeting(self):
        self._confirm_import(self._csv([
            ["2026-12-03", "", "Erstes Thema", "", "open", "", "", "", "", "Text 1"],
            ["2026-12-03", "", "Zweites Thema", "", "open", "", "", "", "", "Text 2"],
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

    def test_logo_upload_has_dedicated_save_action_and_persists_file(self):
        import tempfile
        from django.core.files.uploadedfile import SimpleUploadedFile
        from django.test import override_settings
        from .models import OrganizationSettings

        page = self.client.get(reverse("management_settings"))
        self.assertContains(page, "Logo speichern")
        with tempfile.TemporaryDirectory() as media_root, override_settings(MEDIA_ROOT=media_root):
            response = self.client.post(reverse("management_settings"), {
                "action": "save_logo",
                "logo": SimpleUploadedFile(
                    "organisation.svg",
                    b'<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10"></svg>',
                    content_type="image/svg+xml",
                ),
            })
            self.assertRedirects(response, reverse("management_settings"))
            settings = OrganizationSettings.objects.get(pk=1)
            self.assertTrue(settings.logo.name.endswith("organisation.svg"))
            self.assertTrue(settings.logo.storage.exists(settings.logo.name))
            settings.logo.delete(save=True)

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

    def test_uploaded_organization_logo_is_exposed_to_templates(self):
        from django.core.files.base import ContentFile
        from .access import organization_branding
        from .models import OrganizationSettings

        settings = OrganizationSettings.objects.create(name="Test")
        settings.logo.save("organization.svg", ContentFile(b"<svg xmlns='http://www.w3.org/2000/svg'/>"), save=True)

        branding = organization_branding(None)
        self.assertEqual(branding["organization_logo_url"], reverse("organization_logo"))

        response = self.client.get(reverse("dashboard"))
        self.assertContains(response, "organization-brand-logo")
        self.assertContains(response, branding["organization_logo_url"])

    def test_admin_can_edit_all_colors_and_templates_receive_mode_palette(self):
        from .models import OrganizationSettings
        settings = OrganizationSettings.objects.create(name="Test")
        response = self.client.get(reverse("admin:meetings_organizationsettings_change", args=[settings.pk]))
        self.assertEqual(response.status_code, 200)
        for label in ("Primärfarbe", "Sekundärfarbe", "Tertiärfarbe"):
            self.assertContains(response, label)
        response = self.client.post(reverse("admin:meetings_organizationsettings_change", args=[settings.pk]), {
            "name": "Test", "short_name": "MM", "timezone": "Europe/Berlin", "attachment_max_size_mb": "20",
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


class AgendaFollowupLinkTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username="followup-admin", email="followup-admin@example.com", password="strong-test-password"
        )
        self.client.force_login(self.admin)
        self.series = MeetingSeries.objects.create(name="Wiedervorlage-Reihe")
        self.source_meeting = Meeting.objects.create(series=self.series, date="2026-12-03", title="Ausgangstermin")
        self.first_target = Meeting.objects.create(series=self.series, date="2027-01-14", title="Folgetermin 1")
        self.second_target = Meeting.objects.create(series=self.series, date="2027-02-11", title="Folgetermin 2")
        self.topic = Topic.objects.create(title="Wiedervorlage-Thema", series=self.series)
        self.item = AgendaItem.objects.create(
            meeting=self.source_meeting, topic=self.topic, working_text="Aktueller Sachstand",
            status="in_progress", position=0,
        )

    def _schedule(self, target):
        return self.client.post(reverse("meeting", args=[self.source_meeting.pk]), {
            "item_id": self.item.pk,
            "schedule_item": self.item.pk,
            "target_series": self.series.pk,
            "target_meeting": target.pk,
            "working_text": "Aktueller Sachstand",
        })

    def test_scheduling_creates_followup_and_keeps_source_open(self):
        response = self._schedule(self.first_target)
        self.assertRedirects(response, f"{reverse('meeting', args=[self.source_meeting.pk])}#agenda-item-{self.item.pk}")
        self.item.refresh_from_db()
        followup = AgendaItem.objects.get(followup_of=self.item)
        self.assertEqual(followup.meeting, self.first_target)
        self.assertEqual(followup.working_text, "")
        self.assertEqual(self.item.status, "in_progress")
        self.assertEqual(self.item.meeting, self.source_meeting)
        self.assertEqual(AgendaItem.objects.filter(topic=self.topic).count(), 2)
    
    def test_clearing_existing_followup_deletes_linked_future_agenda_item_after_confirmation(self):
        self._schedule(self.first_target)
        followup = AgendaItem.objects.get(followup_of=self.item)

        response = self.client.post(reverse("meeting", args=[self.source_meeting.pk]), {
            "item_id": self.item.pk,
            "schedule_item": self.item.pk,
            "working_text": "Aktualisierter Text",
            "target_series": self.series.pk,
            "target_meeting": "",
            "confirm_clear_followup": "1",
        })

        self.assertRedirects(response, f"{reverse('meeting', args=[self.source_meeting.pk])}#agenda-item-{self.item.pk}")
        self.item.refresh_from_db()
        self.assertEqual(self.item.working_text, "Aktualisierter Text")
        self.assertFalse(AgendaItem.objects.filter(pk=followup.pk).exists())
        self.assertFalse(AgendaItem.objects.filter(followup_of=self.item).exists())

    def test_clearing_followup_requires_confirmation(self):
        self._schedule(self.first_target)
        followup = AgendaItem.objects.get(followup_of=self.item)

        self.client.post(reverse("meeting", args=[self.source_meeting.pk]), {
            "item_id": self.item.pk,
            "schedule_item": self.item.pk,
            "working_text": self.item.working_text,
            "target_series": self.series.pk,
            "target_meeting": "",
        })

        self.assertTrue(AgendaItem.objects.filter(pk=followup.pk).exists())

    def test_saving_text_without_a_selected_date_does_not_create_followup(self):
        response = self.client.post(reverse("meeting", args=[self.source_meeting.pk]), {
            "item_id": self.item.pk,
            "working_text": "Neuer Sachstand",
        })
        self.assertRedirects(response, f"{reverse('meeting', args=[self.source_meeting.pk])}#agenda-item-{self.item.pk}")
        self.item.refresh_from_db()
        self.assertEqual(self.item.working_text, "Neuer Sachstand")
        self.assertFalse(AgendaItem.objects.filter(followup_of=self.item).exists())

    def test_followup_date_is_blank_by_default(self):
        response = self.client.get(reverse("meeting", args=[self.source_meeting.pk]))
        self.assertContains(response, '<option value="" selected>Keine Wiedervorlage</option>', html=True)

    def test_save_all_texts_can_also_schedule_followup(self):
        other_topic = Topic.objects.create(title="Weiterer Punkt", series=self.series)
        other_item = AgendaItem.objects.create(
            meeting=self.source_meeting, topic=other_topic, working_text="Alter weiterer Text",
        )
        response = self.client.post(reverse("meeting", args=[self.source_meeting.pk]), {
            "save_all_working_texts": "1",
            f"working_text_{self.item.pk}": "Aktualisierter Sachstand",
            f"working_text_{other_item.pk}": "Aktualisierter weiterer Text",
            "schedule_item": str(self.item.pk),
            "target_series": str(self.series.pk),
            "target_meeting": str(self.first_target.pk),
        })
        self.assertRedirects(response, reverse("meeting", args=[self.source_meeting.pk]))
        self.item.refresh_from_db()
        other_item.refresh_from_db()
        self.assertEqual(self.item.working_text, "Aktualisierter Sachstand")
        self.assertEqual(other_item.working_text, "Aktualisierter weiterer Text")
        followup = AgendaItem.objects.get(followup_of=self.item)
        self.assertEqual(followup.working_text, "")

    def test_followup_conflict_does_not_partially_change_topic_or_source_text(self):
        target_series = MeetingSeries.objects.create(name="Andere Wiedervorlage-Reihe")
        conflict = Topic.objects.create(title=self.topic.title, series=target_series)
        target_item = AgendaItem.objects.create(meeting=Meeting.objects.create(
            series=target_series, date="2027-01-14",
        ), topic=conflict, working_text="Unabhängiger Eintrag")
        response = self.client.post(reverse("meeting", args=[self.source_meeting.pk]), {
            "item_id": self.item.pk, "schedule_item": self.item.pk,
            "target_series": target_series.pk, "target_meeting": target_item.meeting_id,
            "working_text": "Darf nicht teilweise gespeichert werden",
        })
        self.assertRedirects(response, f"{reverse('meeting', args=[self.source_meeting.pk])}#agenda-item-{self.item.pk}")
        self.item.refresh_from_db()
        self.topic.refresh_from_db()
        self.assertEqual(self.item.working_text, "Aktueller Sachstand")
        self.assertEqual(self.topic.series, self.series)
        self.assertFalse(AgendaItem.objects.filter(followup_of=self.item).exists())

    def test_changing_target_moves_existing_followup_without_duplicate(self):
        self._schedule(self.first_target)
        followup = AgendaItem.objects.get(followup_of=self.item)
        response = self._schedule(self.second_target)
        self.assertRedirects(response, f"{reverse('meeting', args=[self.source_meeting.pk])}#agenda-item-{self.item.pk}")
        followup.refresh_from_db()
        self.assertEqual(followup.meeting, self.second_target)
        self.assertEqual(AgendaItem.objects.filter(topic=self.topic).count(), 2)
        self.assertFalse(AgendaItem.objects.filter(meeting=self.first_target, topic=self.topic).exists())


class RepositoryConsistencyRegressionTests(TestCase):
    def test_finalize_permission_uses_meeting_series_even_when_topic_ids_collide(self):
        from datetime import date
        reader = User.objects.create_user(username="series-reader", password="strong-test-password")
        meeting_series = MeetingSeries.objects.create(name="Lesereihe")
        unrelated_series = MeetingSeries.objects.create(name="Fremde Reihe")
        SeriesAccess.objects.create(user=reader, series=meeting_series, role=SeriesAccess.ROLE_READER)
        # Make the topic and meeting primary keys collide intentionally.
        unrelated_topic = Topic.objects.create(title="Unabhängiges Thema", series=unrelated_series)
        meeting = Meeting.objects.create(pk=unrelated_topic.pk, series=meeting_series, date=date(2026, 12, 1))
        self.client.force_login(reader)
        response = self.client.post(reverse("finalize", args=[meeting.pk]))
        self.assertEqual(response.status_code, 403)
        meeting.refresh_from_db()
        self.assertIsNone(meeting.finalized_at)

    def test_uploaded_attachment_download_requires_series_access(self):
        import tempfile
        from django.core.files.uploadedfile import SimpleUploadedFile
        from django.test import override_settings
        from .models import TopicAttachment

        series = MeetingSeries.objects.create(name="Dateirechte-Reihe")
        topic = Topic.objects.create(title="Vertraulicher Anhang", series=series)
        allowed = User.objects.create_user(username="file-reader", password="strong-test-password")
        denied = User.objects.create_user(username="other-reader", password="strong-test-password")
        SeriesAccess.objects.create(user=allowed, series=series, role=SeriesAccess.ROLE_READER)
        with tempfile.TemporaryDirectory() as media_root:
            with override_settings(MEDIA_ROOT=media_root):
                attachment = TopicAttachment.objects.create(
                    topic=topic, label="Geheim", uploaded_file=SimpleUploadedFile("secret.txt", b"secret-content"),
                )
                self.client.force_login(denied)
                denied_response = self.client.get(reverse("attachment_download", args=[attachment.pk]))
                self.assertEqual(denied_response.status_code, 404)
                self.client.force_login(allowed)
                allowed_response = self.client.get(reverse("attachment_download", args=[attachment.pk]))
                self.assertEqual(allowed_response.status_code, 200)
                self.assertEqual(b"".join(allowed_response.streaming_content), b"secret-content")

    def test_smb_paths_are_linked_only_when_scheme_and_authority_are_valid(self):
        from .models import TopicAttachment
        topic = Topic.objects.create(title="Netzwerklink")
        valid = TopicAttachment.objects.create(topic=topic, label="Gültig", network_path="smb://fileserver/freigabe/datei.pdf")
        unc = TopicAttachment.objects.create(topic=topic, label="UNC", network_path=r"\\\\fileserver\\freigabe\\datei.pdf")
        unsafe = TopicAttachment.objects.create(topic=topic, label="Unsicher", network_path="javascript:alert(1)")
        self.assertEqual(valid.network_url, "smb://fileserver/freigabe/datei.pdf")
        web_link = TopicAttachment.objects.create(topic=topic, label="Web", network_path="https://intranet.example.org/dokument")
        self.assertEqual(web_link.network_url, "https://intranet.example.org/dokument")
        self.assertTrue(unc.network_url.startswith("smb://fileserver/"))
        self.assertEqual(unsafe.network_url, "")

    def test_protocol_snapshot_status_uses_human_readable_label(self):
        from datetime import date
        from .models import TopicSnapshot
        series = MeetingSeries.objects.create(name="Protokollreihe")
        meeting = Meeting.objects.create(series=series, date=date(2026, 12, 2))
        snapshot = TopicSnapshot.objects.create(
            meeting=meeting, topic_title="Status", text="", status="in_progress", topic_id=42,
        )
        self.assertEqual(snapshot.get_status_display(), "In Arbeit")

    def test_series_reset_preserves_multiple_agenda_entries_for_same_topic(self):
        from datetime import timedelta
        from django.utils import timezone
        today = timezone.localdate()
        first_new_date = today + timedelta(days=7)
        series = MeetingSeries.objects.create(
            name="Reset-Erhaltung", recurrence="weekly", recurrence_interval=1,
            weekday=first_new_date.weekday(), start_date=first_new_date,
            end_date=first_new_date + timedelta(days=14),
        )
        topic = Topic.objects.create(title="Mehrere alte Punkte", series=series)
        old_one = Meeting.objects.create(series=series, date=today + timedelta(days=1))
        old_two = Meeting.objects.create(series=series, date=today + timedelta(days=2))
        AgendaItem.objects.create(meeting=old_one, topic=topic, working_text="Text aus Termin eins", position=0)
        AgendaItem.objects.create(meeting=old_two, topic=topic, working_text="Text aus Termin zwei", position=0)

        moderator = User.objects.create_superuser(
            username="reset-admin", email="reset-admin@example.com", password="strong-test-password",
        )
        self.client.force_login(moderator)
        response = self.client.post(reverse("series_reset_meetings", args=[series.pk]))
        self.assertRedirects(response, reverse("series_edit", args=[series.pk]))
        items = list(AgendaItem.objects.filter(topic=topic).select_related("meeting").order_by("meeting__date"))
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0].meeting.date, first_new_date)
        self.assertEqual(items[0].working_text, "Text aus Termin eins")
        self.assertEqual(items[1].meeting.date, first_new_date + timedelta(days=7))
        self.assertEqual(items[1].working_text, "Text aus Termin zwei")
        self.assertFalse(Meeting.objects.filter(pk__in=[old_one.pk, old_two.pk]).exists())

    def test_recurrence_reconciliation_moves_agenda_to_nearest_generated_meeting(self):
        from datetime import timedelta
        from django.utils import timezone
        from .services import generate_meetings
        today = timezone.localdate()
        first_date = today + timedelta(days=3)
        series = MeetingSeries.objects.create(
            name="Rhythmuswechsel", recurrence="weekly", recurrence_interval=1,
            weekday=first_date.weekday(), start_date=first_date,
            end_date=first_date + timedelta(days=14),
        )
        obsolete_date = today + timedelta(days=1)
        obsolete = Meeting.objects.create(series=series, date=obsolete_date)
        topic = Topic.objects.create(title="Mitnahme", series=series)
        item = AgendaItem.objects.create(
            meeting=obsolete, topic=topic, working_text="Muss erhalten bleiben",
            status="in_progress",
        )
        created = generate_meetings(series)
        item.refresh_from_db()
        self.assertEqual(item.meeting.date, first_date)
        self.assertEqual(item.working_text, "Muss erhalten bleiben")
        self.assertEqual(item.status, "in_progress")
        self.assertFalse(Meeting.objects.filter(pk=obsolete.pk).exists())
        self.assertGreaterEqual(len(created), 1)



class AgendaItemDeletionTests(TestCase):
    def setUp(self):
        from datetime import date
        self.user = User.objects.create_user(username="agenda-editor", password="strong-test-password")
        self.client.force_login(self.user)
        self.series = MeetingSeries.objects.create(name="Löschtest-Reihe")
        SeriesAccess.objects.create(user=self.user, series=self.series)
        self.meeting = Meeting.objects.create(series=self.series, date=date(2026, 12, 1))
        self.other_meeting = Meeting.objects.create(series=self.series, date=date(2026, 12, 8))
        self.topic = Topic.objects.create(title="Bleibendes Thema", series=self.series)
        self.item = AgendaItem.objects.create(meeting=self.meeting, topic=self.topic, working_text="Text für den Termin")
        self.other_item = AgendaItem.objects.create(meeting=self.other_meeting, topic=self.topic, working_text="Text im Folgetermin")

    def test_delete_action_is_only_shown_in_topic_overview(self):
        self.user.is_superuser = True
        self.user.save(update_fields=["is_superuser"])

        meeting_response = self.client.get(reverse("meeting", args=[self.meeting.pk]))
        self.assertEqual(meeting_response.status_code, 200)
        self.assertNotContains(meeting_response, "Punkt löschen")
        self.assertNotContains(meeting_response, "Punkt aus diesem Termin entfernen")

        topic_response = self.client.get(reverse("topic_edit", args=[self.topic.pk]))
        self.assertEqual(topic_response.status_code, 200)
        self.assertContains(topic_response, "Punkt aus diesem Termin entfernen")
        self.assertContains(
            topic_response,
            reverse("agenda_item_delete", args=[self.meeting.pk, self.item.pk]),
        )

    def test_delete_removes_only_selected_meeting_entry_and_keeps_topic(self):
        response = self.client.post(reverse("agenda_item_delete", args=[self.meeting.pk, self.item.pk]))

        self.assertRedirects(response, reverse("topic_edit", args=[self.topic.pk]))
        self.assertFalse(AgendaItem.objects.filter(pk=self.item.pk).exists())
        self.assertTrue(Topic.objects.filter(pk=self.topic.pk).exists())
        self.assertTrue(AgendaItem.objects.filter(pk=self.other_item.pk, topic=self.topic).exists())

    def test_completed_meeting_agenda_item_cannot_be_deleted(self):
        from django.utils import timezone
        self.meeting.finalized_at = timezone.now()
        self.meeting.save(update_fields=["finalized_at"])

        response = self.client.post(reverse("agenda_item_delete", args=[self.meeting.pk, self.item.pk]))

        self.assertRedirects(response, reverse("meeting", args=[self.meeting.pk]))
        self.assertTrue(AgendaItem.objects.filter(pk=self.item.pk).exists())
        self.assertTrue(Topic.objects.filter(pk=self.topic.pk).exists())

    def test_item_from_another_meeting_cannot_be_deleted_through_this_url(self):
        response = self.client.post(reverse("agenda_item_delete", args=[self.meeting.pk, self.other_item.pk]))

        self.assertEqual(response.status_code, 404)
        self.assertTrue(AgendaItem.objects.filter(pk=self.other_item.pk).exists())


class RepositoryAuditRegressionTests(TestCase):
    def test_meeting_delete_merges_status_assignment_and_followup_link(self):
        from datetime import timedelta
        from django.utils import timezone
        from .models import AuditEvent

        today = timezone.localdate()
        series = MeetingSeries.objects.create(name="Punktübernahme")
        moderator = User.objects.create_user(username="merge-moderator", password="strong-test-password")
        retained_assignee = User.objects.create_user(username="retained-owner", password="strong-test-password")
        source_assignee = User.objects.create_user(username="source-owner", password="strong-test-password")
        SeriesAccess.objects.create(user=moderator, series=series, role=SeriesAccess.ROLE_MODERATOR)
        source_meeting = Meeting.objects.create(series=series, date=today + timedelta(days=1))
        target_meeting = Meeting.objects.create(series=series, date=today + timedelta(days=8))
        later_meeting = Meeting.objects.create(series=series, date=today + timedelta(days=15))
        topic = Topic.objects.create(title="Zusammengeführtes Thema", series=series)
        source_item = AgendaItem.objects.create(
            meeting=source_meeting, topic=topic, working_text="Quelltext",
            assigned_to=source_assignee, status="done",
        )
        target_item = AgendaItem.objects.create(
            meeting=target_meeting, topic=topic, working_text="Zieltext",
            assigned_to=retained_assignee, status="open",
        )
        followup = AgendaItem.objects.create(
            meeting=later_meeting, topic=topic, working_text="Wiedervorlage",
            followup_of=source_item,
        )

        self.client.force_login(moderator)
        response = self.client.post(reverse("meeting_delete", args=[source_meeting.pk]))
        self.assertRedirects(response, reverse("series_admin"))

        target_item.refresh_from_db()
        followup.refresh_from_db()
        self.assertEqual(target_item.status, "done")
        self.assertEqual(target_item.assigned_to, retained_assignee)
        self.assertEqual(target_item.working_text, "Zieltext\nQuelltext")
        self.assertEqual(followup.followup_of, target_item)
        self.assertTrue(AuditEvent.objects.filter(
            action="deleted", series=series, summary__contains="Punktübernahme"
        ).exists())

    def test_finalize_rolls_back_partial_snapshots_on_failure(self):
        from datetime import date
        from unittest.mock import patch
        from .models import TopicSnapshot
        from .services import finalize_meeting

        series = MeetingSeries.objects.create(name="Atomarer Abschluss")
        meeting = Meeting.objects.create(series=series, date=date(2026, 12, 20))
        first = Topic.objects.create(title="Erster Snapshot", series=series)
        second = Topic.objects.create(title="Zweiter Snapshot", series=series)
        AgendaItem.objects.create(meeting=meeting, topic=first, working_text="Erster Text")
        AgendaItem.objects.create(meeting=meeting, topic=second, working_text="Zweiter Text")
        manager_class = TopicSnapshot.objects.__class__
        original = manager_class.get_or_create
        calls = 0

        def fail_on_second_snapshot(manager, *args, **kwargs):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise RuntimeError("Simulierter Snapshot-Fehler")
            return original(manager, *args, **kwargs)

        with patch.object(manager_class, "get_or_create", new=fail_on_second_snapshot):
            with self.assertRaises(RuntimeError):
                finalize_meeting(meeting)

        meeting.refresh_from_db()
        self.assertIsNone(meeting.finalized_at)
        self.assertFalse(TopicSnapshot.objects.filter(meeting=meeting).exists())


    def test_finalize_rolls_back_when_audit_event_cannot_be_written(self):
        from datetime import date
        from unittest.mock import patch

        series = MeetingSeries.objects.create(name="Abschluss mit Audit")
        user = User.objects.create_user(username="finalize-user", password="strong-test-password")
        SeriesAccess.objects.create(user=user, series=series, role=SeriesAccess.ROLE_PARTICIPANT)
        meeting = Meeting.objects.create(series=series, date=date(2026, 12, 21))
        topic = Topic.objects.create(title="Abschluss-Thema", series=series)
        AgendaItem.objects.create(meeting=meeting, topic=topic, working_text="Sachstand")

        self.client.force_login(user)
        with patch("meetings.views.record_event", side_effect=RuntimeError("Audit nicht verfügbar")):
            with self.assertRaises(RuntimeError):
                self.client.post(reverse("finalize", args=[meeting.pk]))

        meeting.refresh_from_db()
        self.assertIsNone(meeting.finalized_at)
        from .models import TopicSnapshot
        self.assertFalse(TopicSnapshot.objects.filter(meeting=meeting).exists())



class ApprovedRepositoryAuditFollowupTests(TestCase):
    def test_archive_template_has_balanced_section_elements(self):
        from pathlib import Path
        template = Path(__file__).resolve().parent.parent / "templates" / "meetings" / "archive.html"
        content = template.read_text(encoding="utf-8")
        self.assertEqual(content.count("<section"), content.count("</section>"))

    def test_archived_topic_cannot_be_added_to_meeting_through_post(self):
        from datetime import date
        user = User.objects.create_user(username="archive-member", password="strong-test-password")
        series = MeetingSeries.objects.create(name="Archivschutz")
        SeriesAccess.objects.create(user=user, series=series)
        meeting = Meeting.objects.create(series=series, date=date(2026, 12, 18))
        topic = Topic.objects.create(title="Archiviertes Thema", series=series, status="archived")
        self.client.force_login(user)

        response = self.client.post(
            reverse("meeting", args=[meeting.pk]),
            {"add_existing_topic": topic.pk},
        )

        self.assertRedirects(response, reverse("meeting", args=[meeting.pk]))
        self.assertFalse(AgendaItem.objects.filter(meeting=meeting, topic=topic).exists())

    def test_archived_topics_are_not_carried_forward_from_previous_protocols(self):
        from datetime import date
        from django.utils import timezone
        from .services import ensure_agenda
        series = MeetingSeries.objects.create(name="Archivierter Übertrag")
        topic = Topic.objects.create(title="Nicht mehr übernehmen", series=series, status="archived")
        previous = Meeting.objects.create(
            series=series, date=date(2026, 11, 20), finalized_at=timezone.now()
        )
        AgendaItem.objects.create(meeting=previous, topic=topic, status="open")
        upcoming = Meeting.objects.create(series=series, date=date(2026, 12, 20))

        items = ensure_agenda(upcoming)

        self.assertFalse(items.exists())
        self.assertFalse(AgendaItem.objects.filter(meeting=upcoming, topic=topic).exists())

    def test_topic_csv_rejects_archived_agenda_rows_and_preserves_archived_topic_state(self):
        from datetime import date
        from .topic_csv import parse_topic_agenda_csv
        MeetingSeries.objects.create(name="CSV-Archiv")
        headers = (
            "record_type;series;topic_series;meeting_date;meeting_title;topic_title;"
            "topic_status;archive_previous_status;agenda_status"
        )
        agenda_csv = headers + "\nagenda;CSV-Archiv;CSV-Archiv;2026-12-18;;Archivthema;archived;done;open"
        rows, errors = parse_topic_agenda_csv(agenda_csv)
        self.assertEqual(rows, [])
        self.assertTrue(any("Archivierte Themen dürfen nicht" in error for error in errors))

        topic_csv = headers + "\ntopic;CSV-Archiv;CSV-Archiv;;;Archivthema;archived;done;"
        rows, errors = parse_topic_agenda_csv(topic_csv)
        self.assertEqual(errors, [])
        self.assertEqual(rows[0]["topic"]["archive_previous_status"], "done")

        Topic.objects.create(
            title="Schon archiviert",
            series=MeetingSeries.objects.get(name="CSV-Archiv"),
            status="archived",
        )
        reopened_in_csv = headers + "\nagenda;CSV-Archiv;CSV-Archiv;2026-12-19;;schon archiviert;open;;open"
        rows, errors = parse_topic_agenda_csv(reopened_in_csv)
        self.assertEqual(rows, [])
        self.assertTrue(any("muss zuerst über die Themenansicht" in error for error in errors))

        active_topic = Topic.objects.create(
            title="Mit offenem Termin",
            series=MeetingSeries.objects.get(name="CSV-Archiv"),
            status="open",
        )
        future_meeting = Meeting.objects.create(
            series=active_topic.series, date=date(2026, 12, 23)
        )
        AgendaItem.objects.create(meeting=future_meeting, topic=active_topic)
        archive_in_csv = headers + "\ntopic;CSV-Archiv;CSV-Archiv;;;Mit offenem Termin;archived;open;"
        rows, errors = parse_topic_agenda_csv(archive_in_csv)
        self.assertEqual(rows, [])
        self.assertTrue(any("zukünftigen oder offenen Tagesordnung" in error for error in errors))

    def test_reopening_meeting_keeps_snapshot_responsible_name_in_audit(self):
        from datetime import date
        from django.utils import timezone
        from .models import AuditEvent, TopicSnapshot
        user = User.objects.create_user(username="protocol-moderator", password="strong-test-password")
        series = MeetingSeries.objects.create(name="Snapshot-Reihe")
        SeriesAccess.objects.create(user=user, series=series, role=SeriesAccess.ROLE_MODERATOR)
        meeting = Meeting.objects.create(series=series, date=date(2026, 12, 19), finalized_at=timezone.now())
        TopicSnapshot.objects.create(
            meeting=meeting, topic_title="Verantwortung", text="Stand", status="done",
            topic_id=123, responsible_name="Max Mustermann",
        )
        self.client.force_login(user)

        response = self.client.post(reverse("meeting_reopen", args=[meeting.pk]))

        self.assertRedirects(response, reverse("meeting", args=[meeting.pk]))
        event = AuditEvent.objects.get(meeting=meeting, action="reopened")
        self.assertEqual(
            event.changes["Gesicherter Protokollstand"][0]["responsible_name"],
            "Max Mustermann",
        )

    def test_deleted_series_name_is_kept_on_retained_meetings(self):
        from datetime import date
        from .views import _meeting_series_name
        user = User.objects.create_user(username="series-moderator", password="strong-test-password")
        series = MeetingSeries.objects.create(name="Historische Fachrunde")
        SeriesAccess.objects.create(user=user, series=series, role=SeriesAccess.ROLE_MODERATOR)
        meeting = Meeting.objects.create(series=series, date=date(2026, 1, 15))
        self.client.force_login(user)

        response = self.client.post(reverse("series_delete", args=[series.pk]))

        self.assertRedirects(response, reverse("dashboard"))
        meeting.refresh_from_db()
        self.assertIsNone(meeting.series_id)
        self.assertEqual(meeting.archived_series_name, "Historische Fachrunde")
        self.assertEqual(_meeting_series_name(meeting), "Historische Fachrunde")
        self.assertEqual(str(meeting), "Historische Fachrunde – 15.01.2026")
        protocol = self.client.get(reverse("protocol", args=[meeting.pk]))
        self.assertContains(protocol, "Historische Fachrunde")

    def test_topic_csv_sample_rows_match_the_header(self):
        import csv
        import io
        from .topic_csv import sample_csv_response
        response = sample_csv_response()
        rows = list(csv.reader(
            io.StringIO(response.content.decode("utf-8-sig")),
            delimiter=";",
        ))
        self.assertEqual(len(rows[0]), 16)
        for row in rows[1:4]:
            self.assertEqual(len(row), len(rows[0]))

    def test_user_csv_identity_conflicts_are_rejected_before_import(self):
        from .user_csv import _resolve_existing_users
        User.objects.create_user(
            username="first-account", email="first@example.org", password="strong-test-password"
        )
        User.objects.create_user(
            username="second-account", email="second@example.org", password="strong-test-password"
        )
        grouped = [
            ("first-account", {"values": {"email": "second@example.org"}}),
        ]
        resolved, errors = _resolve_existing_users(grouped)
        self.assertEqual(resolved, {})
        self.assertTrue(any("gehören zu unterschiedlichen Konten" in error for error in errors))

        grouped = [
            ("renamed-first", {"values": {"email": "first@example.org"}}),
            ("renamed-second", {"values": {"email": "first@example.org"}}),
        ]
        resolved, errors = _resolve_existing_users(grouped)
        self.assertTrue(any(
            "dasselbe Benutzerkonto" in error or "mehreren CSV-Benutzern" in error
            for error in errors
        ))

        grouped = [
            ("new-user-a", {"values": {"email": "new@example.org"}}),
            ("new-user-b", {"values": {"email": "new@example.org"}}),
        ]
        resolved, errors = _resolve_existing_users(grouped)
        self.assertTrue(any("mehreren CSV-Benutzern" in error for error in errors))

    def test_meeting_delete_message_matches_the_action(self):
        from datetime import date
        user = User.objects.create_superuser(
            username="orphan-meeting-moderator",
            email="orphan@example.org",
            password="strong-test-password",
        )
        meeting = Meeting.objects.create(series=None, date=date(2026, 12, 22))
        self.client.force_login(user)
        response = self.client.post(reverse("meeting_delete", args=[meeting.pk]))
        self.assertRedirects(response, reverse("meeting", args=[meeting.pk]))
        from django.contrib.messages import get_messages
        stored_messages = [str(message) for message in get_messages(response.wsgi_request)]
        self.assertIn(
            "Dieser Termin gehört zu keiner Besprechungsreihe und kann daher nicht gelöscht werden.",
            stored_messages,
        )


class UserOverviewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="profile-user", password="old-strong-password",
            first_name="Ada", last_name="Beispiel", email="ada@example.test",
        )
        self.series = MeetingSeries.objects.create(name="Profil-Reihe")
        SeriesAccess.objects.create(
            user=self.user, series=self.series, role=SeriesAccess.ROLE_READER
        )
        self.client.force_login(self.user)

    def test_user_overview_shows_series_role_and_profile_fields(self):
        response = self.client.get(reverse("user_overview"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ada")
        self.assertContains(response, "ada@example.test")
        self.assertContains(response, "Profil-Reihe")
        self.assertContains(response, "Leser")
        self.assertNotContains(response, "Admin – globaler Zugriff")

    def test_user_overview_does_not_autofocus_old_password_field(self):
        response = self.client.get(reverse("user_overview"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'name="old_password" autofocus')

    def test_series_role_and_request_share_one_column_with_hidden_submit_button(self):
        response = self.client.get(reverse("user_overview"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<th>Berechtigung</th>", html=True)
        self.assertNotContains(response, "<th>Deine Berechtigung</th>", html=True)
        self.assertContains(response, 'id="role-%s"' % self.series.pk)
        self.assertContains(response, 'data-current-role="reader"')
        self.assertContains(response, '<button type="submit" hidden>Antrag senden</button>', html=True)

    def test_user_can_edit_own_profile(self):
        response = self.client.post(reverse("user_overview"), {
            "form_type": "profile",
            "first_name": "Grace",
            "last_name": "Hopper",
            "email": "grace@example.test",
            "short_description": "Projektleitung",
        })
        self.assertRedirects(response, reverse("user_overview"))
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Grace")
        self.assertEqual(self.user.last_name, "Hopper")
        self.assertEqual(self.user.email, "grace@example.test")
        self.assertEqual(self.user.meeting_profile.short_description, "Projektleitung")

    def test_user_can_change_own_password_without_losing_session(self):
        response = self.client.post(reverse("user_overview"), {
            "form_type": "password",
            "old_password": "old-strong-password",
            "new_password1": "New-strong-password-123",
            "new_password2": "New-strong-password-123",
        })
        self.assertRedirects(response, reverse("user_overview"))
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("New-strong-password-123"))
        self.assertEqual(int(self.client.session["_auth_user_id"]), self.user.pk)

    def test_admin_sees_global_access_for_all_series(self):
        from django.contrib.auth.models import Group
        admin_group, _ = Group.objects.get_or_create(name="Admin")
        self.user.groups.add(admin_group)
        response = self.client.get(reverse("user_overview"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Admin – globaler Zugriff")
        self.assertEqual(len(response.context["series_rows"]), MeetingSeries.objects.count())


class SeriesAccessRequestTests(TestCase):
    def setUp(self):
        from .models import SeriesAccessRequest
        self.SeriesAccessRequest = SeriesAccessRequest
        self.requester = User.objects.create_user(username="requester", password="strong-test-password")
        self.moderator = User.objects.create_user(username="series-moderator", password="strong-test-password")
        self.series = MeetingSeries.objects.create(name="Antragsreihe")
        self.other_series = MeetingSeries.objects.create(name="Andere Reihe")
        SeriesAccess.objects.create(
            user=self.moderator, series=self.series, role=SeriesAccess.ROLE_MODERATOR
        )

    def test_user_sees_all_series_and_can_request_permission(self):
        self.client.force_login(self.requester)
        page = self.client.get(reverse("user_overview"))
        self.assertContains(page, "Antragsreihe")
        self.assertContains(page, "Andere Reihe")
        self.assertContains(page, "Keine Berechtigung")
        response = self.client.post(reverse("user_overview"), {
            "form_type": "access_request", "series_id": self.series.pk,
            "role": SeriesAccess.ROLE_MODERATOR,
        })
        self.assertRedirects(response, reverse("user_overview"))
        self.assertTrue(self.SeriesAccessRequest.objects.filter(
            user=self.requester, series=self.series,
            requested_role=SeriesAccess.ROLE_MODERATOR,
            status=self.SeriesAccessRequest.STATUS_PENDING,
        ).exists())

    def test_lower_role_request_is_automatically_approved_and_applied(self):
        SeriesAccess.objects.create(
            user=self.requester, series=self.series, role=SeriesAccess.ROLE_MODERATOR
        )
        self.client.force_login(self.requester)

        response = self.client.post(reverse("user_overview"), {
            "form_type": "access_request", "series_id": self.series.pk,
            "role": SeriesAccess.ROLE_READER,
        })

        self.assertRedirects(response, reverse("user_overview"))
        access = SeriesAccess.objects.get(user=self.requester, series=self.series)
        self.assertEqual(access.role, SeriesAccess.ROLE_READER)
        access_request = self.SeriesAccessRequest.objects.get(
            user=self.requester, series=self.series
        )
        self.assertEqual(access_request.status, self.SeriesAccessRequest.STATUS_APPROVED)
        self.assertEqual(access_request.requested_role, SeriesAccess.ROLE_READER)
        self.assertIsNotNone(access_request.decided_at)
        self.assertIsNone(access_request.decided_by)

    def test_only_one_pending_request_per_user_and_series(self):
        self.client.force_login(self.requester)
        payload = {
            "form_type": "access_request", "series_id": self.series.pk,
            "role": SeriesAccess.ROLE_READER,
        }
        self.client.post(reverse("user_overview"), payload)
        self.client.post(reverse("user_overview"), {**payload, "role": SeriesAccess.ROLE_PARTICIPANT})
        self.assertEqual(self.SeriesAccessRequest.objects.filter(
            user=self.requester, series=self.series,
            status=self.SeriesAccessRequest.STATUS_PENDING,
        ).count(), 1)

    def test_moderator_can_approve_request_for_own_series(self):
        access_request = self.SeriesAccessRequest.objects.create(
            user=self.requester, series=self.series,
            requested_role=SeriesAccess.ROLE_PARTICIPANT,
        )
        self.client.force_login(self.moderator)
        response = self.client.post(reverse("series_admin"), {
            "form_type": "access_request_decision", "request_id": access_request.pk,
            "decision": "approved", "decision_note": "Zustimmung",
        })
        self.assertRedirects(response, reverse("series_admin"))
        access_request.refresh_from_db()
        self.assertEqual(access_request.status, self.SeriesAccessRequest.STATUS_APPROVED)
        self.assertEqual(access_request.decision_note, "Zustimmung")
        self.assertTrue(SeriesAccess.objects.filter(
            user=self.requester, series=self.series,
            role=SeriesAccess.ROLE_PARTICIPANT,
        ).exists())

    def test_moderator_cannot_process_request_for_another_series(self):
        access_request = self.SeriesAccessRequest.objects.create(
            user=self.requester, series=self.other_series,
            requested_role=SeriesAccess.ROLE_READER,
        )
        self.client.force_login(self.moderator)
        response = self.client.post(reverse("series_admin"), {
            "form_type": "access_request_decision", "request_id": access_request.pk,
            "decision": "rejected",
        })
        self.assertEqual(response.status_code, 403)
        access_request.refresh_from_db()
        self.assertEqual(access_request.status, self.SeriesAccessRequest.STATUS_PENDING)


class DashboardStatusFilterTests(TestCase):
    def setUp(self):
        from datetime import date

        self.user = User.objects.create_user(
            username="dashboard-filter-user", password="strong-test-password"
        )
        self.series = MeetingSeries.objects.create(name="Dashboard-Filter-Reihe")
        SeriesAccess.objects.create(user=self.user, series=self.series)
        meeting = Meeting.objects.create(series=self.series, date=date(2026, 12, 1))
        self.open_topic = Topic.objects.create(title="Status Offen", series=self.series)
        self.in_progress_topic = Topic.objects.create(title="Status In Arbeit", series=self.series)
        self.done_topic = Topic.objects.create(title="Status Erledigt", series=self.series)
        AgendaItem.objects.create(
            meeting=meeting, topic=self.open_topic, assigned_to=self.user, status="open"
        )
        AgendaItem.objects.create(
            meeting=meeting, topic=self.in_progress_topic, assigned_to=self.user, status="in_progress"
        )
        AgendaItem.objects.create(
            meeting=meeting, topic=self.done_topic, assigned_to=self.user, status="done"
        )
        self.client.force_login(self.user)

    def test_dashboard_defaults_to_open_and_in_progress_agenda_items(self):
        response = self.client.get(reverse("dashboard"), {"due": ""})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            set(response.context["topics"]),
            {self.open_topic, self.in_progress_topic},
        )
        self.assertEqual(response.context["selected_status"], "active")
        self.assertContains(response, "Offen oder in Arbeit")
        self.assertNotContains(response, "Status Erledigt")

    def test_dashboard_keeps_explicit_single_status_filters(self):
        response = self.client.get(reverse("dashboard"), {"status": "open", "due": ""})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context["topics"]), [self.open_topic])
        self.assertEqual(response.context["selected_status"], "open")

        response = self.client.get(reverse("dashboard"), {"status": "in_progress", "due": ""})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context["topics"]), [self.in_progress_topic])
        self.assertEqual(response.context["selected_status"], "in_progress")


class DeploymentUpdatePermissionTests(TestCase):
    def setUp(self):
        from django.contrib.auth.models import Group

        self.admin = User.objects.create_user(
            username="deployment-admin", password="strong-test-password"
        )
        admin_group, _ = Group.objects.get_or_create(name="Admin")
        self.admin.groups.add(admin_group)
        self.member = User.objects.create_user(
            username="deployment-member", password="strong-test-password"
        )

    def test_only_global_admin_can_open_update_page(self):
        self.client.force_login(self.member)
        response = self.client.get(reverse("deployment_updates"))
        self.assertEqual(response.status_code, 403)

        self.client.force_login(self.admin)
        response = self.client.get(reverse("deployment_updates"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Software aktualisieren")
        self.assertContains(response, "Zielversion")

    def test_non_admin_cannot_start_an_update(self):
        self.client.force_login(self.member)
        response = self.client.post(reverse("deployment_updates"), {"branch": "beta"})
        self.assertEqual(response.status_code, 403)

    def test_invalid_branch_is_rejected(self):
        self.client.force_login(self.admin)
        response = self.client.post(reverse("deployment_updates"), {"branch": "feature/other"})
        self.assertEqual(response.status_code, 302)

    def test_admin_starts_only_the_selected_supported_branch(self):
        from unittest.mock import patch

        info = {
            "deployment_type": "Debian / systemd",
            "current_branch": "beta",
            "current_commit_date": "2026-11-23T12:00:00+00:00",
            "current_image": "",
            "build_created": "",
            "update_available": True,
            "availability_message": "",
        }
        self.client.force_login(self.admin)
        with patch("meetings.views._deployment_info", return_value=info), \
             patch("meetings.views._available_update_branches", return_value=["beta", "main"]), \
             patch("meetings.views._read_update_status", return_value={"status": "idle"}), \
             patch("meetings.views.os.path.exists", return_value=False), \
             patch("meetings.views.subprocess.run") as start:
            start.return_value.returncode = 0
            start.return_value.stderr = ""
            response = self.client.post(reverse("deployment_updates"), {"branch": "beta"})

        self.assertEqual(response.status_code, 302)
        start.assert_called_once()
        self.assertEqual(
            start.call_args.args[0],
            ["sudo", "-n", "/usr/local/sbin/meeting-manager-update", "beta"],
        )


class OrganizationLogoDeliveryTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="logo-viewer", password="strong-test-password"
        )
        self.admin = User.objects.create_superuser(
            username="logo-admin", email="logo-admin@example.test",
            password="strong-test-password",
        )

    def test_logo_endpoint_requires_login(self):
        response = self.client.get(reverse("organization_logo"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_logo_is_served_from_private_media_storage_to_signed_in_users(self):
        import tempfile
        from pathlib import Path
        from django.core.files.base import ContentFile
        from django.test import override_settings
        from .models import OrganizationSettings

        with tempfile.TemporaryDirectory() as media_dir:
            with override_settings(MEDIA_ROOT=media_dir):
                organization = OrganizationSettings.objects.create(name="Testorganisation")
                organization.logo.save(
                    "logo.svg",
                    ContentFile(b'<svg xmlns="http://www.w3.org/2000/svg"></svg>'),
                    save=True,
                )
                self.client.force_login(self.user)

                response = self.client.get(reverse("organization_logo"))

                self.assertEqual(response.status_code, 200)
                self.assertEqual(response["Content-Type"], "image/svg+xml")
                self.assertEqual(response["Cache-Control"], "private, no-store")
                self.assertEqual(b"".join(response.streaming_content), b'<svg xmlns="http://www.w3.org/2000/svg"></svg>')

    def test_branding_context_uses_application_route_not_media_url(self):
        import tempfile
        from django.core.files.base import ContentFile
        from django.test import override_settings
        from .models import OrganizationSettings

        with tempfile.TemporaryDirectory() as media_dir:
            with override_settings(MEDIA_ROOT=media_dir):
                organization = OrganizationSettings.objects.create(name="Testorganisation")
                organization.logo.save("logo.png", ContentFile(b"not-a-real-png"), save=True)
                self.client.force_login(self.user)

                response = self.client.get(reverse("dashboard"))

                self.assertEqual(
                    response.context["organization_logo_url"],
                    reverse("organization_logo"),
                )

                rendered = response.content.decode()
                self.assertEqual(
                    rendered.count('class="brand-icon organization-brand-logo"'),
                    2,
                )

    def test_invalid_configured_organization_logo_does_not_silently_disappear(self):
        import tempfile
        from datetime import date
        from django.core.files.base import ContentFile
        from django.test import override_settings
        from .models import Meeting, MeetingSeries, OrganizationSettings

        with tempfile.TemporaryDirectory() as media_dir:
            with override_settings(MEDIA_ROOT=media_dir):
                organization = OrganizationSettings.objects.create(name="Testorganisation")
                organization.logo.save(
                    "broken.svg",
                    ContentFile(b"<svg><not-valid-svg"),
                    save=True,
                )
                series = MeetingSeries.objects.create(name="Testreihe")
                meeting = Meeting.objects.create(series=series, date=date(2026, 11, 23))
                self.client.force_login(self.admin)

                response = self.client.get(reverse("protocol_pdf", args=[meeting.pk]))

                self.assertEqual(response.status_code, 503)
                self.assertIn("Organisationslogo", response.content.decode("utf-8"))
                self.assertNotEqual(response.status_code, 500)

    def test_protocol_pdf_without_configured_logo_still_downloads(self):
        from datetime import date
        from .models import Meeting, MeetingSeries

        series = MeetingSeries.objects.create(name="Testreihe")
        meeting = Meeting.objects.create(series=series, date=date(2026, 11, 23))
        self.client.force_login(self.admin)

        response = self.client.get(reverse("protocol_pdf", args=[meeting.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")
        self.assertEqual(response["Content-Disposition"], 'attachment; filename="Protokoll_Testreihe_2026-11-23.pdf"')
        self.assertTrue(response.content.startswith(b"%PDF"))

    def test_logo_settings_upload_creates_png_copy_for_svg(self):
        import tempfile
        from django.core.files.uploadedfile import SimpleUploadedFile
        from django.test import override_settings
        from .models import OrganizationSettings

        with tempfile.TemporaryDirectory() as media_dir:
            with override_settings(MEDIA_ROOT=media_dir):
                self.client.force_login(self.admin)
                svg_data = (
                    b'<svg xmlns="http://www.w3.org/2000/svg" width="120" height="40">'
                    b'<rect width="120" height="40" fill="#00549f"/></svg>'
                )
                response = self.client.post(
                    reverse("management_settings"),
                    {"action": "save_logo", "logo": SimpleUploadedFile("organization.svg", svg_data, content_type="image/svg+xml")},
                )
                self.assertEqual(response.status_code, 302)
                organization = OrganizationSettings.objects.get(pk=1)
                self.assertTrue(organization.logo.name.endswith(".svg"))
                self.assertTrue(organization.logo_png.name.endswith(".png"))
                organization.logo_png.open("rb")
                try:
                    self.assertTrue(organization.logo_png.read().startswith(b"\x89PNG\r\n\x1a\n"))
                finally:
                    organization.logo_png.close()

    def test_reuploading_svg_replaces_previous_png_and_removes_old_file(self):
        import tempfile
        from django.core.files.uploadedfile import SimpleUploadedFile
        from django.test import override_settings
        from .models import OrganizationSettings

        with tempfile.TemporaryDirectory() as media_dir:
            with override_settings(MEDIA_ROOT=media_dir):
                self.client.force_login(self.admin)

                def upload_svg(fill):
                    svg_data = (
                        '<svg xmlns="http://www.w3.org/2000/svg" width="120" height="40">'
                        f'<rect width="120" height="40" fill="{fill}"/></svg>'
                    ).encode()
                    return self.client.post(
                        reverse("management_settings"),
                        {"action": "save_logo", "logo": SimpleUploadedFile(
                            "organization.svg", svg_data, content_type="image/svg+xml"
                        )},
                    )

                self.assertEqual(upload_svg("#00549f").status_code, 302)
                organization = OrganizationSettings.objects.get(pk=1)
                first_png_name = organization.logo_png.name
                organization.logo_png.open("rb")
                try:
                    first_png_data = organization.logo_png.read()
                finally:
                    organization.logo_png.close()

                self.assertEqual(upload_svg("#ff0000").status_code, 302)
                organization.refresh_from_db()
                self.assertNotEqual(organization.logo_png.name, first_png_name)
                organization.logo_png.open("rb")
                try:
                    second_png_data = organization.logo_png.read()
                finally:
                    organization.logo_png.close()

                self.assertNotEqual(second_png_data, first_png_data)
                self.assertFalse(organization.logo.storage.exists(first_png_name))
                self.assertTrue(organization.logo.storage.exists(organization.logo_png.name))

    def test_organization_logo_is_embedded_in_protocol_pdf(self):
        import tempfile
        from datetime import date
        from django.core.files.base import ContentFile
        from django.test import override_settings
        from .models import Meeting, MeetingSeries, OrganizationSettings

        with tempfile.TemporaryDirectory() as media_dir:
            with override_settings(MEDIA_ROOT=media_dir):
                organization = OrganizationSettings.objects.create(name="Testorganisation")
                svg_data = (
                    b'<svg xmlns="http://www.w3.org/2000/svg" width="120" height="40">'
                    b'<rect width="120" height="40" fill="#00549f"/></svg>'
                )
                organization.logo.save("logo.svg", ContentFile(svg_data), save=True)
                import cairosvg
                organization.logo_png.save(
                    "logo.png",
                    ContentFile(cairosvg.svg2png(bytestring=svg_data, output_width=1600)),
                    save=True,
                )
                series = MeetingSeries.objects.create(name="Testreihe")
                meeting = Meeting.objects.create(series=series, date=date(2026, 11, 23))
                self.client.force_login(self.admin)

                response = self.client.get(reverse("protocol_pdf", args=[meeting.pk]))

                self.assertEqual(response.status_code, 200)
                self.assertEqual(response["Content-Type"], "application/pdf")
                self.assertIn(b"/Subtype /Image", response.content)
