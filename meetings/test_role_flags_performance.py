from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser, Group
from django.test import RequestFactory, TestCase

from .access import role_flags
from .models import MeetingSeries, SeriesAccess
from .user_roles import sync_user_role

User = get_user_model()


class RoleFlagsPerformanceTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.series = MeetingSeries.objects.create(name="Role-Flags-Reihe")

    def test_regular_user_role_flags_use_two_queries(self):
        user = User.objects.create_user(username="role-flags-user", password="test-password")
        SeriesAccess.objects.create(user=user, series=self.series, role=SeriesAccess.ROLE_READER)
        request = self.factory.get("/")
        request.user = user

        with self.assertNumQueries(2):
            flags = role_flags(request)

        self.assertFalse(flags["is_admin"])
        self.assertFalse(flags["is_auditor"])
        self.assertFalse(flags["is_moderator"])
        self.assertTrue(flags["is_reader"])
        self.assertFalse(flags["can_view_open_topics"])

    def test_admin_can_also_have_series_moderator_flags(self):
        user = User.objects.create_user(username="role-flags-admin", password="test-password")
        sync_user_role(user, "admin")
        SeriesAccess.objects.create(user=user, series=self.series, role=SeriesAccess.ROLE_MODERATOR)
        request = self.factory.get("/")
        request.user = user

        with self.assertNumQueries(2):
            flags = role_flags(request)

        self.assertTrue(flags["is_admin"])
        self.assertTrue(flags["is_moderator"])
        self.assertFalse(flags["is_reader"])
        self.assertTrue(flags["can_view_open_topics"])

    def test_auditor_role_flags_require_only_one_query(self):
        user = User.objects.create_user(username="role-flags-auditor", password="test-password")
        sync_user_role(user, "auditor")
        request = self.factory.get("/")
        request.user = user

        with self.assertNumQueries(1):
            flags = role_flags(request)

        self.assertTrue(flags["is_auditor"])
        self.assertFalse(flags["is_admin"])
        self.assertFalse(flags["is_moderator"])
        self.assertFalse(flags["can_view_open_topics"])

    def test_anonymous_role_flags_do_not_query_the_database(self):
        request = self.factory.get("/")
        request.user = AnonymousUser()

        with self.assertNumQueries(0):
            flags = role_flags(request)

        self.assertFalse(any(flags.values()))
