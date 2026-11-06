from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from .models import MeetingSeries, Topic, TopicTransferHistory

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


from datetime import timedelta
from django.utils import timezone
from .models import Meeting
from .services import generate_meetings


class MeetingCalendarTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username="calendar-admin", password="strong-test-password", is_staff=True
        )
        self.member = User.objects.create_user(
            username="calendar-member", password="strong-test-password"
        )
        self.series = MeetingSeries.objects.create(
            name="Kalender-Reihe",
            recurrence="weekly",
            start_date=timezone.localdate(),
        )

    def test_calendar_is_visible_to_all_logged_in_users(self):
        self.client.force_login(self.member)
        response = self.client.get(reverse("calendar"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Terminkalender")

    def test_only_admin_can_create_a_meeting(self):
        self.client.force_login(self.member)
        response = self.client.post(reverse("calendar"), {
            "action": "create",
            "series": self.series.pk,
            "date": timezone.localdate() + timedelta(days=2),
            "title": "Zusatztermin",
        })
        self.assertEqual(response.status_code, 403)
        self.assertFalse(Meeting.objects.filter(title="Zusatztermin").exists())

    def test_admin_can_create_and_move_an_unfinalized_meeting(self):
        self.client.force_login(self.admin)
        original_date = timezone.localdate() + timedelta(days=7)
        response = self.client.post(reverse("calendar"), {
            "action": "create",
            "series": self.series.pk,
            "date": original_date,
            "title": "Planung",
        })
        self.assertRedirects(response, reverse("calendar"))
        meeting = Meeting.objects.get(series=self.series, date=original_date)
        new_date = original_date + timedelta(days=1)
        response = self.client.post(reverse("meeting_date_edit", args=[meeting.pk]), {
            "date": new_date,
            "title": "Verschoben",
        })
        self.assertRedirects(response, reverse("calendar"))
        meeting.refresh_from_db()
        self.assertEqual(meeting.date, new_date)
        self.assertEqual(meeting.title, "Verschoben")

    def test_admin_cannot_change_finalized_meeting(self):
        self.client.force_login(self.admin)
        meeting = Meeting.objects.create(
            series=self.series,
            date=timezone.localdate() + timedelta(days=7),
            finalized_at=timezone.now(),
        )
        response = self.client.post(reverse("meeting_date_edit", args=[meeting.pk]), {
            "date": timezone.localdate() + timedelta(days=8),
            "title": "Änderungsversuch",
        })
        self.assertRedirects(response, reverse("protocol", args=[meeting.pk]))
        meeting.refresh_from_db()
        self.assertEqual(meeting.date, timezone.localdate() + timedelta(days=7))

    def test_generation_catches_up_from_old_series_start_date(self):
        self.series.start_date = timezone.localdate() - timedelta(days=120)
        self.series.save(update_fields=["start_date"])
        created = generate_meetings(self.series, count=4)
        self.assertEqual(len(created), 4)
        self.assertTrue(all(item.date >= timezone.localdate() for item in created))
        self.assertEqual(
            [item.date for item in created],
            sorted(item.date for item in created),
        )

    def test_monthly_generation_keeps_end_of_month_anchor(self):
        series = MeetingSeries.objects.create(
            name="Monatsreihe 31",
            recurrence="monthly",
            start_date=timezone.localdate().replace(day=31)
            if timezone.localdate().day == 31
            else timezone.localdate().replace(day=1) + timedelta(days=30),
        )
        created = generate_meetings(series, count=3)
        self.assertEqual(len(created), 3)
        self.assertEqual(created[0].date.day, series.start_date.day)
        if created[0].date.month == 1:
            self.assertEqual(created[1].date.day, 28 if not created[1].date.year % 4 else 28)
