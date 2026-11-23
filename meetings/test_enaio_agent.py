from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import EnaioAgent

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
