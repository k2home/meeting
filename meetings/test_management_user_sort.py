from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

User = get_user_model()


class ManagementUserSortTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username="user-sort-admin", email="sort-admin@example.test",
            password="strong-test-password",
        )
        self.first = User.objects.create_user(
            username="first-login", password="strong-test-password"
        )
        self.second = User.objects.create_user(
            username="second-login", password="strong-test-password"
        )
        now = timezone.now()
        User.objects.filter(pk=self.first.pk).update(last_login=now - timedelta(days=10))
        User.objects.filter(pk=self.second.pk).update(last_login=now - timedelta(days=1))

    def test_sort_by_last_login_places_recently_active_users_first(self):
        self.client.force_login(self.admin)

        response = self.client.get(reverse("management_users"), {"sort": "last_login"})

        self.assertEqual(response.status_code, 200)
        usernames = [item["account"].username for item in response.context["users"]]
        self.assertLess(usernames.index("second-login"), usernames.index("first-login"))
        self.assertEqual(response.context["selected_sort"], "last_login")

    def test_invalid_sort_falls_back_to_name_order(self):
        self.client.force_login(self.admin)

        response = self.client.get(reverse("management_users"), {"sort": "password"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["selected_sort"], "name")
