from hashlib import sha256
import json
from pathlib import Path
import tempfile
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class SecurityDescriptionPdfTests(TestCase):
    def test_pdf_requires_authentication(self):
        response = self.client.get(reverse("security_description_pdf"))
        self.assertEqual(response.status_code, 302)

    def test_authenticated_user_can_download_pdf(self):
        user = get_user_model().objects.create_user(
            username="security-doc-reader", password="Strong-test-password-123!"
        )
        self.client.force_login(user)

        response = self.client.get(reverse("security_description_pdf"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")
        self.assertIn("attachment;", response["Content-Disposition"])
        self.assertEqual(response["Cache-Control"], "private, no-store")
        self.assertTrue(response.content.startswith(b"%PDF-"))
        self.assertGreater(len(response.content), 10_000)


class SecurityDescriptionPageTests(TestCase):
    def test_security_review_page_requires_authentication(self):
        response = self.client.get(reverse("security_description"))
        self.assertEqual(response.status_code, 302)

    def test_authenticated_user_sees_full_review_and_pdf_link(self):
        user = get_user_model().objects.create_user(
            username="security-review-reader", password="Strong-test-password-123!"
        )
        self.client.force_login(user)

        response = self.client.get(reverse("security_description"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Rollen- und Berechtigungskonzept")
        self.assertContains(response, "Konkrete Maßnahmen und empfohlene Vorgehensweisen")
        self.assertContains(response, reverse("security_description_pdf"))
        self.assertContains(response, "Inhaltsverzeichnis")
        self.assertContains(response, 'href="#1-kurzbeschreibung-und-zweck"')
        self.assertContains(response, 'class="toc"')

    @patch("meetings.views._debian_testing_mode_enabled", return_value=True)
    def test_review_marking_tools_are_only_rendered_in_testing_mode(self, _testing_mode):
        user = get_user_model().objects.create_user(
            username="security-review-marker", password="Strong-test-password-123!"
        )
        self.client.force_login(user)

        response = self.client.get(reverse("security_description"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Taste <kbd>M</kbd>")
        self.assertNotContains(response, 'id="add-review-mark"')
        self.assertContains(response, 'event.key.toLowerCase() !== "m"')
        self.assertContains(response, 'id="export-review-marks"')
        self.assertContains(response, "localStorage")
        self.assertContains(response, "Prüfmarkierungen")


class TestDocumentationPageTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="test-documentation-reader", password="Strong-test-password-123!"
        )
        self.client.force_login(self.user)

    def test_test_documentation_requires_authentication(self):
        self.client.logout()
        for method, route in (
            (self.client.get, "test_documentation"),
            (self.client.get, "test_documentation_status"),
            (self.client.get, "test_documentation_download"),
        ):
            response = method(reverse(route))
            self.assertEqual(response.status_code, 302)
        response = self.client.post(
            reverse("test_documentation_toggle"),
            data="{}",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 302)

    @patch("meetings.guide_views._test_documentation_testing_mode_enabled", return_value=False)
    def test_checklist_is_read_only_outside_testing_mode(self, _testing_mode):
        response = self.client.get(reverse("test_documentation"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Prüfung des Verfahrens")
        self.assertContains(response, 'type="checkbox"')
        self.assertContains(response, "Test erfolgreich")
        self.assertContains(response, "Lesemodus")
        self.assertContains(response, "disabled")
        self.assertNotContains(response, 'data-save-url')
        self.assertNotContains(response, 'id="test-documentation-config"')

        self.assertEqual(
            self.client.post(
                reverse("test_documentation_toggle"),
                data=json.dumps({"line": 1, "occurrence": 1, "checked": True, "revision": "0" * 64}),
                content_type="application/json",
            ).status_code,
            403,
        )
        self.assertEqual(self.client.get(reverse("test_documentation_download")).status_code, 403)
        self.assertEqual(self.client.get(reverse("test_documentation_status")).status_code, 403)

    @patch("meetings.guide_views._test_documentation_testing_mode_enabled", return_value=True)
    def test_toggle_rejects_non_object_and_invalid_checkbox_payloads(self, _testing_mode):
        for payload in ("[]", '"text"', "null", "{}"):
            with self.subTest(payload=payload):
                response = self.client.post(
                    reverse("test_documentation_toggle"),
                    data=payload,
                    content_type="application/json",
                )
                self.assertEqual(response.status_code, 400)

        for payload in (
            {"line": 0, "occurrence": 1, "checked": True, "revision": "0" * 64},
            {"line": 1, "occurrence": 0, "checked": True, "revision": "0" * 64},
            {"line": 1, "occurrence": 1, "checked": "true", "revision": "0" * 64},
            {"line": 1, "occurrence": 1, "checked": True, "revision": "invalid"},
        ):
            response = self.client.post(
                reverse("test_documentation_toggle"),
                data=json.dumps(payload),
                content_type="application/json",
            )
            self.assertEqual(response.status_code, 400)

    @patch("meetings.guide_views._test_documentation_testing_mode_enabled", return_value=True)
    def test_toggle_requires_csrf_token(self, _testing_mode):
        from django.test import Client

        client = Client(enforce_csrf_checks=True)
        client.force_login(self.user)
        page = client.get(reverse("test_documentation"))
        self.assertEqual(page.status_code, 200)
        response = client.post(
            reverse("test_documentation_toggle"),
            data=json.dumps({"line": 1, "occurrence": 1, "checked": True, "revision": "0" * 64}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)

    @patch("meetings.guide_views._test_documentation_testing_mode_enabled", return_value=True)
    def test_testing_mode_enables_shared_editing_and_markdown_download(self, _testing_mode):
        response = self.client.get(reverse("test_documentation"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "TESTING-Modus ist aktiv")
        self.assertContains(response, 'data-save-url="' + reverse("test_documentation_toggle") + '"')
        self.assertContains(response, reverse("test_documentation_status"))
        self.assertContains(response, reverse("test_documentation_download"))
        self.assertContains(response, "spätestens nach zwei Sekunden")
        self.assertNotContains(response, 'localStorage.setItem("test-documentation')

    def test_markdown_checklist_keeps_lists_and_result_sections_separate(self):
        response = self.client.get(reverse("test_documentation"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<ul>")
        self.assertContains(response, "<li>")
        self.assertContains(response, "<p><strong>Ergebnisprüfung</strong></p>")
        self.assertContains(response, "keine automatische Moderator- oder Leseberechtigung")
        self.assertContains(response, "Verbindliche Zugriffsprüfung je Funktionsbereich und Rolle")
        self.assertContains(response, "Ist die Seite nicht erreichbar und ist die Zugriffsverweigerung nachgewiesen, ist die Prüfung dieses Funktionsbereichs für diese Rolle beendet.")
        self.assertContains(response, "Bei gesperrter übergeordneter Seite wird zum nächsten Funktionsbereich gewechselt.")
        self.assertContains(response, "Besprechungsreihe bearbeiten – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)")
        self.assertContains(response, "Abgeschlossene Besprechung wieder öffnen – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)")
        self.assertContains(response, "Themen als CSV exportieren – Prüfrolle: Moderator*in (Serienrolle der geprüften Reihe)")
        self.assertContains(response, "Fehlende Serienberechtigung prüfen – Prüfrolle: globale Nutzerrolle + Moderator*in ausschließlich in einer anderen Reihe")
        self.assertContains(response, "Globaler Admin mit Moderatorzuweisung in Testreihe A")
        self.assertContains(response, "Moderatorzugriff auf eine fremde Reihe verweigern")
        self.assertContains(response, "Besprechungsreihe bearbeiten – Prüfrolle: globale Nutzerrolle + Moderator*in der geprüften Reihe")
        self.assertContains(response, "9.3.2 Besprechungsreihe bearbeiten – Prüfrolle: globaler Admin")
        self.assertContains(response, "9.8.4 Abgeschlossene Besprechung wieder öffnen – Prüfrolle: globaler Admin")
        self.assertContains(response, "5.3.1 Zugriff auf die Serienverwaltung prüfen – Prüfrolle: Nutzer*in ohne Serienzuweisung")
        self.assertContains(response, "4.10.1 Serienberechtigung beantragen – Prüfrolle: globale Nutzerrolle ohne Serienzuweisung")
        self.assertContains(response, "6.3.1 Zugriff auf die Serienverwaltung prüfen – Prüfrolle: Leser*in (Serienrolle)")
        self.assertContains(response, "7.3.1 Zugriff auf die Serienverwaltung prüfen – Prüfrolle: Teilnehmer*in (Serienrolle)")
        self.assertContains(response, "10.3.1 Zugriff auf die Serienverwaltung prüfen – Prüfrolle: globale Auditor*in")
        self.assertNotContains(response, "Besprechungsreihe verlängern – Prüfrolle: Nutzer*in ohne Serienzuweisung")
        self.assertNotContains(response, "Besprechungsreihe bearbeiten – Prüfrolle: Leser*in (Serienrolle)")
        self.assertNotContains(response, "Besprechungsreihe löschen – Prüfrolle: Teilnehmer*in (Serienrolle)")
        self.assertNotContains(response, "Berechtigungen einer Reihe verwalten – Prüfrolle: globale Auditor*in")
        self.assertContains(response, "<p><strong>Test erfolgreich:</strong>")
        self.assertNotContains(response, "<h2><strong>Test erfolgreich:</strong>")
        self.assertContains(response, "document-content ul")
        self.assertContains(response, "document-content hr")
        self.assertContains(response, "3.2.3 Testcheckliste aus Hilfe &amp; Anleitung öffnen")
        for phase in ("Installation", "Ersteinrichtung", "Testing", "Produktiv – Globale Rolle Nutzer", "Produktiv – Ohne Berechtigungen", "Produktiv – Leser", "Produktiv – Teilnehmer", "Produktiv – Moderator", "Produktiv – Globale Rolle Admin", "Produktiv – Globale Rolle Auditor"):
            self.assertContains(response, f'id="{phase.lower()}"')
        self.assertContains(response, 'class="card test-document-index"')
        self.assertContains(response, 'class="test-document-layout"')
        self.assertContains(response, '.test-document-index .toc>ul>li:first-child> a{display:none}')
        self.assertContains(response, '.test-document-index .toc>ul>li>ul>li>ul>li.is-current>ul{display:block}')
        self.assertContains(response, 'querySelectorAll(\":scope > ul > li > ul > li > ul > li\")')
        self.assertContains(response, 'window.addEventListener("scroll", updateCurrentSection')
        self.assertContains(response, '.test-document-index .toc li.is-complete>a{background:#dcffdc')
        self.assertContains(response, ':root[data-theme="dark"] .test-document-index .toc li.is-complete>a{background:hsl(120,25%,24%)}')
        self.assertContains(response, 'const completionByCheckbox = new WeakMap()')
        self.assertContains(response, 'window.updateTestDocumentationCompletionForCheckbox = updateCompletionForCheckbox;')
        self.assertContains(response, 'setInterval(refresh, 2000)')
        self.assertContains(response, 'spätestens nach zwei Sekunden')
        self.assertContains(response, 'item.classList.toggle("is-complete"')
        self.assertContains(response, 'updateCompletionForCheckbox(checkbox, !desired, desired);')
        for anchor in ("installation", "ersteinrichtung", "testing", "produktiv-globale-rolle-nutzer", "produktiv-ohne-berechtigungen", "produktiv-leser", "produktiv-teilnehmer", "produktiv-moderator", "produktiv-globale-rolle-admin", "produktiv-globale-rolle-auditor"):
            self.assertContains(response, f'href="#{anchor}"')
        self.assertContains(response, '<h3 id="1-anmeldung-und-sitzung">1. Anmeldung und Sitzung</h3>')
        self.assertContains(response, "<h4 id=")
        self.assertContains(response, "1.1 Anmeldung mit gültigem Konto")

    def test_all_productive_role_cases_have_explicit_steps_and_results(self):
        from meetings.guide_views import _test_documentation_source_path

        lines = Path(_test_documentation_source_path()).read_text(encoding="utf-8").splitlines()
        for index, heading in enumerate(lines):
            if not heading.startswith("#### ") or not heading[5:7] in {"4.", "5.", "6.", "7.", "8.", "9.", "10"}:
                continue
            end = index + 1
            while end < len(lines) and not lines[end].startswith(("#### ", "### ", "## ")):
                end += 1
            block = lines[index:end]
            self.assertIn("**Prüfschritt**", block, heading)
            result_index = next((i for i, line in enumerate(block) if line == "**Ergebnisprüfung**"), -1)
            self.assertGreaterEqual(result_index, 0, heading)
            result_checks = [
                line for line in block[result_index + 1:]
                if line.startswith("- ")
            ]
            self.assertTrue(result_checks, f"{heading} benötigt konkrete Ergebnisprüfungen")
            self.assertTrue(
                all(line.startswith("- [ ] ") or line == "- **Test erfolgreich:** [ ]" for line in result_checks),
                f"{heading} muss anklickbare Ergebnisprüfungen verwenden",
            )

    def test_denied_role_cases_have_matching_steps_and_result_checks(self):
        from meetings.guide_views import _test_documentation_source_path

        lines = Path(_test_documentation_source_path()).read_text(encoding="utf-8").splitlines()
        for index, heading in enumerate(lines):
            if not heading.startswith("#### ") or not heading[5:7] in {"4.", "5.", "6.", "7.", "8.", "9.", "10"}:
                continue
            end = index + 1
            while end < len(lines) and not lines[end].startswith(("#### ", "### ", "## ")):
                end += 1
            block = lines[index:end]
            permission = next((line for line in block if line.startswith("**Berechtigungserwartung")), "")
            if "Zugriff verweigert" not in permission:
                continue

            result_index = next((i for i, line in enumerate(block) if line == "**Ergebnisprüfung**"), -1)
            self.assertGreaterEqual(result_index, 0, heading)
            steps = block[:result_index]
            self.assertTrue(
                "**Prüfschritt**" in steps or any(line.startswith("- [ ] ") for line in steps),
                f"{heading} benötigt einen konkreten Prüfschritt oder eine Zugriffs-Checkliste",
            )
            result_checks = [
                line for line in block[result_index + 1:]
                if line.startswith("- ")
            ]
            self.assertTrue(result_checks, f"{heading} benötigt eine Ergebnisprüfung")
            self.assertTrue(
                all(line.startswith("- [ ] ") for line in result_checks),
                f"{heading} muss anklickbare Ergebnisprüfungen verwenden",
            )

    def test_role_specific_access_expectations_match_reachable_empty_views(self):
        from meetings.guide_views import _test_documentation_source_path

        document = Path(_test_documentation_source_path()).read_text(encoding="utf-8")
        self.assertIn("5.4.1 Terminübersicht aufrufen", document)
        self.assertIn("Berechtigungserwartung für Ohne Berechtigungen: Zugriff erlaubt.", document)
        self.assertIn("9.9.2 Archiv aufrufen – Prüfrolle: globaler Admin", document)
        self.assertIn("Berechtigungserwartung für Globale Rolle Auditor: Zugriff verweigert.", document)

    def test_archived_topic_retention_view_is_role_scoped(self):
        from meetings.guide_views import _test_documentation_source_path

        document = Path(_test_documentation_source_path()).read_text(encoding="utf-8")
        self.assertIn("5.13.2 Aufbewahrungsfrist archivierter Themen prüfen", document)
        self.assertIn("6.13.2 Aufbewahrungsfrist archivierter Themen prüfen", document)
        self.assertIn("7.13.2 Aufbewahrungsfrist archivierter Themen prüfen", document)
        self.assertIn("8.13.2 Aufbewahrungsfrist archivierter Themen prüfen", document)
        self.assertIn("9.13.2 Aufbewahrungsfrist archivierter Themen prüfen", document)
        self.assertIn("Archivierte Themen der zugewiesenen Reihe und deren Aufbewahrungsdaten werden angezeigt.", document)
        self.assertIn("Ohne Serienzuweisung enthält die Liste keine archivierten Themen.", document)
        self.assertIn("Zugriff auf das Serienarchiv nicht erlaubt.", document)
        self.assertIn("Weiterleitung zur Auditor*innenübersicht", document)

    def test_checklist_source_path_can_be_configured_for_docker_volume(self):
        from meetings.guide_views import _test_documentation_source_path

        with patch.dict("os.environ", {"TEST_DOCUMENTATION_SOURCE_PATH": "/app/local-test-docs/checklist.md"}):
            self.assertEqual(
                _test_documentation_source_path(),
                Path("/app/local-test-docs/checklist.md"),
            )

    def test_checklist_lock_path_can_be_configured_for_deployment(self):
        from meetings.guide_views import (
            _test_documentation_lock_directory,
            _test_documentation_lock_path,
        )

        source = Path("/opt/meeting-manager/docs/checklist.md")
        with patch.dict("os.environ", {"TEST_DOCUMENTATION_LOCK_PATH": "/var/lib/meeting-manager-updater/test-documentation.lock"}):
            self.assertEqual(
                _test_documentation_lock_path(source),
                Path("/var/lib/meeting-manager-updater/test-documentation.lock"),
            )
            self.assertEqual(
                _test_documentation_lock_directory(source),
                Path("/var/lib/meeting-manager-updater"),
            )

    def test_user_guide_links_to_test_documentation(self):
        response = self.client.get(reverse("user_guide"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse("test_documentation"))
        self.assertContains(response, "Prüfung des Verfahrens – Testcheckliste")

    def test_checklist_structure_revision_ignores_checkbox_state_but_detects_content_changes(self):
        from meetings.guide_views import _checklist_structure_revision

        self.assertEqual(
            _checklist_structure_revision("- [ ] Offener Punkt\n"),
            _checklist_structure_revision("- [x] Offener Punkt\n"),
        )
        self.assertNotEqual(
            _checklist_structure_revision("- [ ] Offener Punkt\n"),
            _checklist_structure_revision("- [ ] Neuer Punkt\n"),
        )

    def test_markdown_checkbox_rendering_respects_existing_status_and_edit_mode(self):
        from meetings.guide_views import _render_test_documentation_markers

        source = "- [ ] Noch offen\n**Test erfolgreich:** [ ]\n- [x] Bereits erfolgreich\n"
        editable = _render_test_documentation_markers(source, True)
        readonly = _render_test_documentation_markers(source, False)

        self.assertIn('data-checklist-line="1"', editable)
        self.assertIn('class="test-checklist-box test-success-checkbox"', editable)
        self.assertIn('class="test-checklist-box"', editable)
        self.assertIn('data-checklist-occurrence="1"', editable)
        self.assertIn(" checked>", editable)
        self.assertNotIn(" disabled", editable)
        self.assertIn(" disabled>", readonly)

    @patch("meetings.guide_views._test_documentation_testing_mode_enabled", return_value=True)
    def test_checkbox_is_saved_to_local_markdown_and_visible_in_status_and_download(self, _testing_mode):
        from meetings.guide_views import _checklist_revision

        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "checklist.md"
            original = "- [ ] Testschritt\n- [ ] Weiterer Schritt\n"
            source.write_text(original, encoding="utf-8")
            with patch("meetings.guide_views._test_documentation_source_path", return_value=source):
                page = self.client.get(reverse("test_documentation"))
                self.assertEqual(page.status_code, 200)

                response = self.client.post(
                    reverse("test_documentation_toggle"),
                    data=json.dumps({
                        "line": 1, "occurrence": 1, "checked": True,
                        "revision": _checklist_revision(original),
                    }),
                    content_type="application/json",
                )

                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.json()["success"])
                self.assertEqual(source.read_text(encoding="utf-8"), "- [x] Testschritt\n- [ ] Weiterer Schritt\n")

                status = self.client.get(reverse("test_documentation_status"))
                self.assertEqual(status.status_code, 200)
                self.assertTrue(status.json()["statuses"]["line-1-1"])

                download = self.client.get(reverse("test_documentation_download"))
                self.assertEqual(download.status_code, 200)
                self.assertIn(b"- [x] Testschritt", download.content)
                self.assertIn("attachment;", download["Content-Disposition"])

    @patch("meetings.guide_views._test_documentation_testing_mode_enabled", return_value=True)
    def test_stale_revision_is_rejected_without_overwriting_other_users_change(self, _testing_mode):
        from meetings.guide_views import _checklist_revision

        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "checklist.md"
            current = "- [x] Bereits geaendert\n"
            source.write_text(current, encoding="utf-8")
            with patch("meetings.guide_views._test_documentation_source_path", return_value=source):
                response = self.client.post(
                    reverse("test_documentation_toggle"),
                    data=json.dumps({
                        "line": 1, "occurrence": 1, "checked": False,
                        "revision": _checklist_revision("- [ ] Alter Stand\n"),
                    }),
                    content_type="application/json",
                )

                self.assertEqual(response.status_code, 409)
                self.assertEqual(source.read_text(encoding="utf-8"), current)
                self.assertTrue(response.json()["statuses"]["line-1-1"])

