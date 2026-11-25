import json

from django.contrib.auth import get_user_model
from django.test import TestCase

from .audit import record_event


class ExternalAuditLogTests(TestCase):
    def test_record_event_emits_metadata_only_json_log(self):
        user = get_user_model().objects.create_user(
            username="audit-log-test",
            password="test-password",
        )

        with self.assertLogs("meetings.security_audit", level="INFO") as captured:
            event = record_event(
                actor=user,
                action="updated",
                summary="Vertraulicher Freitext darf nicht im Infrastruktur-Log stehen",
                changes={"Kommentar": {"vorher": "intern", "nachher": "geheim"}},
            )

        payload = json.loads(captured.records[0].getMessage())
        self.assertEqual(payload["event"], "meeting_manager.audit")
        self.assertEqual(payload["audit_id"], event.pk)
        self.assertEqual(payload["actor_id"], user.pk)
        self.assertEqual(payload["action"], "updated")
        self.assertEqual(payload["scope"], event.scope)
        self.assertNotIn("summary", payload)
        self.assertNotIn("changes", payload)
        self.assertNotIn("Vertraulicher Freitext", captured.records[0].getMessage())
        self.assertNotIn("geheim", captured.records[0].getMessage())
