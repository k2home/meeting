from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class ManagementUserStatusFilterTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username="user-status-admin", email="status-admin@example.test",
            password="strong-test-password",
        )
        self.active_user = User.objects.create_user(
            username="active-person", password="strong-test-password", is_active=True
        )
        self.inactive_user = User.objects.create_user(
            username="inactive-person", password="strong-test-password", is_active=False
        )

    def test_inactive_filter_shows_only_deactivated_accounts(self):
        self.client.force_login(self.admin)

        response = self.client.get(reverse("management_users"), {"status": "inactive"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "inactive-person")
        self.assertNotContains(response, "<td>active-person</td>")
        self.assertEqual(response.context["selected_status"], "inactive")

    def test_invalid_status_filter_falls_back_to_all_users(self):
        self.client.force_login(self.admin)

        response = self.client.get(reverse("management_users"), {"status": "unknown"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "inactive-person")
        self.assertContains(response, "active-person")
        self.assertEqual(response.context["selected_status"], "all")
