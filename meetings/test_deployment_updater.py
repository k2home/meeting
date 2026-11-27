from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from django.conf import settings
from django.test import SimpleTestCase


class DeploymentUpdaterTests(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        module_path = Path(settings.BASE_DIR) / "deploy" / "docker-update-agent.py"
        spec = spec_from_file_location("meeting_docker_update_agent", module_path)
        cls.docker_agent = module_from_spec(spec)
        spec.loader.exec_module(cls.docker_agent)

    def test_docker_update_replaces_checklist_after_image_selection_is_persisted(self):
        events = []

        def compose(*args, image=None, timeout=180):
            events.append(("compose", args, image))
            return SimpleNamespace(stdout="", stderr="", returncode=0)

        def persist(image):
            events.append(("persist", image))
            return None

        def write_state(**changes):
            events.append(("state", changes))

        with (
            patch.object(self.docker_agent, "compose", side_effect=compose),
            patch.object(self.docker_agent, "preserve_running_image", return_value="rollback-image"),
            patch.object(self.docker_agent, "persist_selected_image", side_effect=persist),
            patch.object(self.docker_agent, "write_state", side_effect=write_state),
            patch.object(self.docker_agent, "remove_rollback_image"),
        ):
            self.docker_agent.run_update("beta")

        persist_index = next(i for i, event in enumerate(events) if event[0] == "persist")
        checklist_index = next(
            i for i, event in enumerate(events)
            if event[0] == "compose"
            and event[1][0:3] == ("exec", "-T", "app")
            and "flock -x /app/local-test-docs" in event[1][-1]
        )
        self.assertLess(persist_index, checklist_index)
        checklist_command = events[checklist_index][1][-1]
        self.assertIn("install -m 0660", checklist_command)
        self.assertIn(".checklist-update.$", checklist_command)
        self.assertIn("mv -f", checklist_command)
        self.assertIn("/app/docs/Pruefung-des-Verfahrens-Testdokumentation.md", checklist_command)
        self.assertIn("/app/local-test-docs/Pruefung-des-Verfahrens-Testdokumentation.md", checklist_command)
        self.assertTrue(any(
            event[0] == "state" and event[1].get("status") == "success"
            for event in events
        ))

    def test_docker_checklist_copy_failure_rolls_back_without_persisting_new_image(self):
        events = []

        def compose(*args, image=None, timeout=180):
            events.append(("compose", args, image))
            failed = args[0:3] == ("exec", "-T", "app") and "flock -x /app/local-test-docs" in args[-1]
            return SimpleNamespace(
                stdout="",
                stderr="copy failed" if failed else "",
                returncode=1 if failed else 0,
            )

        def write_state(**changes):
            events.append(("state", changes))

        with (
            patch.object(self.docker_agent, "compose", side_effect=compose),
            patch.object(self.docker_agent, "preserve_running_image", return_value="rollback-image"),
            patch.object(self.docker_agent, "persist_selected_image") as persist,
            patch.object(self.docker_agent, "write_state", side_effect=write_state),
            patch.object(self.docker_agent, "remove_rollback_image"),
        ):
            self.docker_agent.run_update("beta")

        persist.assert_not_called()
        self.assertTrue(any(
            event[0] == "compose"
            and event[1][0:4] == ("up", "-d", "--no-deps", "app")
            and event[2] == "rollback-image"
            for event in events
        ))
        self.assertTrue(any(
            event[0] == "state" and event[1].get("status") == "error"
            and "Testdokumentation" in event[1].get("message", "")
            for event in events
        ))

    def test_debian_update_checks_worktree_and_fetch_before_discarding_checklist(self):
        script = (Path(settings.BASE_DIR) / "deploy" / "update.sh").read_text(encoding="utf-8")
        diff_check = script.index('if ! git -C "$APP_DIR" diff --quiet')
        untracked_check = script.index('UNTRACKED_FILES=')
        fetch = script.index('git -C "$APP_DIR" fetch --prune')
        checklist_reset = script.index('git -C "$APP_DIR" reset -q HEAD -- "$CHECKLIST_RELATIVE"')

        self.assertLess(diff_check, checklist_reset)
        self.assertLess(untracked_check, checklist_reset)
        self.assertLess(fetch, checklist_reset)
        self.assertIn('":(exclude)$CHECKLIST_RELATIVE"', script)
