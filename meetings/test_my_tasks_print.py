from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import MeetingSeries, SeriesAccess, Topic

User = get_user_model()


class PersonalTaskPrintTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="print-task-user", password="strong-test-password"
        )
        self.series = MeetingSeries.objects.create(name="Drucktest-Reihe")
        SeriesAccess.objects.create(user=self.user, series=self.series)
        Topic.objects.create(
            title="Druckbare Aufgabe",
            series=self.series,
            assigned_to=self.user,
        )

    def test_personal_tasks_page_offers_a_print_action_and_print_heading(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("my_tasks"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'onclick="window.print()"')
        self.assertContains(response, "Aufgaben drucken")
        self.assertContains(response, "print-only")
        self.assertContains(response, "Druckbare Aufgabe")

    def test_personal_tasks_print_action_is_not_exposed_to_anonymous_users(self):
        response = self.client.get(reverse("my_tasks"))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)
