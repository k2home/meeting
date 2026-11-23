from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
import hashlib
import secrets
from django.urls import reverse

from .models import EnaioAgent, EnaioFolderSelection

User = get_user_model()


class EnaioAgentPairingTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="enaio-user", password="strong-test-password")

    def test_pairing_code_is_one_time_and_registers_device(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("enaio_agent_pair_code"))
        self.assertEqual(response.status_code, 200)
        code = response.json()["pairing_code"]

        registered = self.client.post(
            reverse("enaio_agent_register"),
            data={"pairing_code": code, "device_name": "Test workstation"},
            content_type="application/json",
        )
        self.assertEqual(registered.status_code, 200)
        self.assertIn("device_token", registered.json())
        agent = EnaioAgent.objects.get(user=self.user)
        self.assertTrue(agent.device_token_hash)
        self.assertEqual(agent.device_name, "Test workstation")
        self.assertFalse(agent.pairing_code_hash)

        repeated = self.client.post(
            reverse("enaio_agent_register"),
            data={"pairing_code": code},
            content_type="application/json",
        )
        self.assertEqual(repeated.status_code, 403)

    def test_agent_poll_requires_device_token(self):
        response = self.client.get(reverse("enaio_agent_next_job"))
        self.assertEqual(response.status_code, 403)


class EnaioAgentLeaseTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="enaio-lease-user", password="strong-test-password")
        self.raw_token = secrets.token_urlsafe(32)
        EnaioAgent.objects.create(
            user=self.user,
            device_token_hash=hashlib.sha256(self.raw_token.encode()).hexdigest(),
        )
        self.auth = {"HTTP_AUTHORIZATION": "Bearer " + self.raw_token}

    def test_folder_selection_is_leased_to_only_one_poll(self):
        selection = EnaioFolderSelection.objects.create(
            user=self.user,
            token_hash=hashlib.sha256(secrets.token_urlsafe(32).encode()).hexdigest(),
            expires_at=timezone.now() + timedelta(minutes=5),
        )

        first = self.client.get(reverse("enaio_agent_next_job"), **self.auth)
        self.assertEqual(first.status_code, 200)
        job = first.json()["job"]
        self.assertEqual(job["selection_id"], selection.pk)
        self.assertTrue(job["lease_token"])

        second = self.client.get(reverse("enaio_agent_next_job"), **self.auth)
        self.assertIsNone(second.json()["job"])

    def test_folder_selection_completion_requires_current_lease(self):
        selection = EnaioFolderSelection.objects.create(
            user=self.user,
            token_hash=hashlib.sha256(secrets.token_urlsafe(32).encode()).hexdigest(),
            expires_at=timezone.now() + timedelta(minutes=5),
        )
        claimed = self.client.get(reverse("enaio_agent_next_job"), **self.auth).json()["job"]
        payload = {
            "folder_id": "123", "folder_type": 1, "folder_name": "Protokolle",
            "folder_path": "/Ablage/Protokolle", "lease_token": claimed["lease_token"],
        }
        completed = self.client.post(
            reverse("enaio_agent_selection_complete", args=[selection.pk]),
            data=payload, content_type="application/json", **self.auth,
        )
        self.assertEqual(completed.status_code, 200)
        selection.refresh_from_db()
        self.assertIsNotNone(selection.consumed_at)


    def test_agent_job_status_reports_active_lease(self):
        selection = EnaioFolderSelection.objects.create(
            user=self.user,
            token_hash=hashlib.sha256(secrets.token_urlsafe(32).encode()).hexdigest(),
            expires_at=timezone.now() + timedelta(minutes=5),
        )
        job = self.client.get(reverse("enaio_agent_next_job"), **self.auth).json()["job"]
        status_url = reverse("enaio_agent_job_status", args=["selection", selection.pk])
        active = self.client.get(status_url, {"lease": job["lease_token"]}, **self.auth)
        self.assertEqual(active.status_code, 200)
        self.assertTrue(active.json()["active"])

        selection.refresh_from_db()
        selection.consumed_at = timezone.now()
        selection.save(update_fields=["consumed_at"])
        inactive = self.client.get(status_url, {"lease": job["lease_token"]}, **self.auth)
        self.assertEqual(inactive.status_code, 200)
        self.assertFalse(inactive.json()["active"])

    def test_browser_cancellation_invalidates_agent_lease(self):
        selection = EnaioFolderSelection.objects.create(
            user=self.user,
            token_hash=hashlib.sha256(secrets.token_urlsafe(32).encode()).hexdigest(),
            expires_at=timezone.now() + timedelta(minutes=5),
        )
        job = self.client.get(reverse("enaio_agent_next_job"), **self.auth).json()["job"]

        self.user.is_superuser = True
        self.user.save(update_fields=["is_superuser"])
        self.client.force_login(self.user)
        cancelled = self.client.post(reverse("enaio_folder_selection_cancel", args=[selection.pk]))
        self.assertEqual(cancelled.status_code, 200)
        selection.refresh_from_db()
        self.assertIsNotNone(selection.consumed_at)
        self.assertIn("abgebrochen", selection.error_message)

        inactive = self.client.get(
            reverse("enaio_agent_job_status", args=["selection", selection.pk]),
            {"lease": job["lease_token"]}, **self.auth,
        )
        self.assertEqual(inactive.status_code, 200)
        self.assertFalse(inactive.json()["active"])
