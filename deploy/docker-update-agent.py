#!/usr/bin/env python3
"""Restricted Docker Compose updater exposed only through a Unix socket."""
import json
import os
import grp
import re
import stat
import subprocess
import threading
import time
from http.server import BaseHTTPRequestHandler
from socketserver import ThreadingMixIn, UnixStreamServer
from pathlib import Path

APP_DIR = Path("/opt/meeting-manager")
COMPOSE_FILE = APP_DIR / "docker" / "compose.yaml"
STATE_FILE = Path("/var/lib/meeting-manager-updater/status.json")
LOCK = threading.Lock()
UPDATE_LOCK = threading.Lock()
REPOSITORY_URL = "https://github.com/k2home/meeting.git"
BRANCH_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]{0,119}$")


def available_branches():
    result = subprocess.run(
        ["/usr/bin/git", "ls-remote", "--heads", REPOSITORY_URL],
        text=True, capture_output=True, timeout=15, check=False,
    )
    if result.returncode:
        raise RuntimeError("Die verfügbaren Git-Branches konnten nicht geladen werden.")
    branches = []
    for line in result.stdout.splitlines():
        parts = line.split("\t", 1)
        if len(parts) != 2 or not parts[1].startswith("refs/heads/"):
            continue
        name = parts[1][len("refs/heads/"):]
        if BRANCH_PATTERN.fullmatch(name) and ".." not in name and not name.endswith(("/", ".")):
            branches.append(name)
    return sorted(set(branches), key=str.casefold)


def read_state():
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"status": "idle", "branch": None, "started_at": None, "finished_at": None, "message": "Noch kein Update ausgeführt.", "log": ""}


def write_state(**changes):
    with LOCK:
        state = read_state()
        state.update(changes)
        STATE_FILE.parent.mkdir(mode=0o750, parents=True, exist_ok=True)
        temporary = STATE_FILE.with_suffix(".tmp")
        temporary.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")
        os.chown(temporary, 0, grp.getgrnam("meeting-update").gr_gid)
        os.chmod(temporary, 0o640)
        temporary.replace(STATE_FILE)
        return state


def compose(*args, image=None, timeout=180):
    env = os.environ.copy()
    if image:
        env["MEETING_IMAGE"] = image
    return subprocess.run(
        ["/usr/bin/docker", "compose", "--project-directory", str(APP_DIR), "-f", str(COMPOSE_FILE), *args],
        cwd=APP_DIR, env=env, text=True, capture_output=True, timeout=timeout, check=False,
    )


def preserve_running_image():
    result = compose("ps", "-q", "app", timeout=30)
    if result.returncode or not result.stdout.strip():
        return None
    container_id = result.stdout.strip().splitlines()[0]
    inspect = subprocess.run(
        ["/usr/bin/docker", "inspect", "--format", "{{.Image}}", container_id],
        text=True, capture_output=True, timeout=30, check=False,
    )
    if inspect.returncode or not inspect.stdout.strip():
        raise RuntimeError("Das bisherige App-Image kann nicht gesichert werden.")
    rollback_ref = "meeting-manager-rollback:" + container_id[:12]
    tag = subprocess.run(
        ["/usr/bin/docker", "image", "tag", inspect.stdout.strip(), rollback_ref],
        text=True, capture_output=True, timeout=30, check=False,
    )
    if tag.returncode:
        raise RuntimeError("Das bisherige App-Image kann nicht für einen Rollback markiert werden.")
    return rollback_ref


def remove_rollback_image(image_ref):
    if image_ref:
        try:
            subprocess.run(
                ["/usr/bin/docker", "image", "rm", image_ref],
                text=True, capture_output=True, timeout=30, check=False,
            )
        except subprocess.SubprocessError:
            pass


def persist_selected_image(image_ref):
    env_file = APP_DIR / ".env"
    if env_file.is_symlink() or not env_file.is_file():
        raise RuntimeError("Die lokale Docker-.env-Datei fehlt oder ist kein reguläres File.")
    original = env_file.read_text(encoding="utf-8")
    lines = original.splitlines()
    replacement = "MEETING_IMAGE=" + image_ref
    found = False
    updated = []
    for line in lines:
        if re.match(r"^\s*MEETING_IMAGE\s*=", line):
            if not found:
                updated.append(replacement)
                found = True
        else:
            updated.append(line)
    if not found:
        updated.append(replacement)

    backup = STATE_FILE.parent / "compose-env.backup"
    backup.write_text(original, encoding="utf-8")
    os.chmod(backup, 0o600)
    try:
        with env_file.open("w", encoding="utf-8") as target:
            target.write("\n".join(updated) + "\n")
            target.flush()
            os.fsync(target.fileno())
    except Exception:
        with env_file.open("w", encoding="utf-8") as target:
            target.write(original)
            target.flush()
            os.fsync(target.fileno())
        backup.unlink(missing_ok=True)
        raise
    return backup


def recover_environment_backup():
    backup = STATE_FILE.parent / "compose-env.backup"
    if not backup.is_file():
        return
    previous_state = read_state()
    if previous_state.get("status") != "success":
        env_file = APP_DIR / ".env"
        if env_file.is_file() and not env_file.is_symlink():
            with env_file.open("w", encoding="utf-8") as target:
                target.write(backup.read_text(encoding="utf-8"))
                target.flush()
                os.fsync(target.fileno())
    backup.unlink(missing_ok=True)


def run_update(branch):
    started = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    write_state(status="running", branch=branch, started_at=started, finished_at=None, message="Update wird ausgeführt.", log="")
    log = []
    previous_image = None
    environment_backup = None
    try:
        previous_image = preserve_running_image()
        image_tag = "latest" if branch == "main" else re.sub(r"[^a-z0-9_.-]+", "-", branch.lower()).strip("-")
        target_image = f"ghcr.io/k2home/meeting:{image_tag}"
        result = compose("pull", "app", image=target_image, timeout=900)
        log.append(result.stdout + result.stderr)
        if result.returncode:
            raise RuntimeError("Das neue Image konnte nicht geladen werden.")
        result = compose("up", "-d", "--no-deps", "app", image=target_image, timeout=240)
        log.append(result.stdout + result.stderr)
        if result.returncode:
            raise RuntimeError("Der Anwendungscontainer konnte nicht aktualisiert werden.")
        healthy = False
        for _ in range(12):
            result = compose("exec", "-T", "app", "sh", "-c", "python manage.py check && python manage.py migrate --check && python -c 'import socket; socket.create_connection((\"127.0.0.1\", 8000), timeout=3).close()'", timeout=30)
            log.append(result.stdout + result.stderr)
            if result.returncode == 0:
                healthy = True
                break
            time.sleep(5)
        if not healthy:
            raise RuntimeError("Die Django-Prüfung war nach dem Update nicht erfolgreich.")

        environment_backup = persist_selected_image(target_image)

        # The repository checklist is authoritative. Replace the persistent
        # volume copy only after the new container is healthy and its image
        # selection has been persisted; local checkbox progress is discarded.
        checklist_copy = compose(
            "exec", "-T", "app", "sh", "-c",
            "flock -x /app/local-test-docs sh -c 'install -m 0660 "
            "/app/docs/Pruefung-des-Verfahrens-Testdokumentation.md "
            "/app/local-test-docs/Pruefung-des-Verfahrens-Testdokumentation.md'",
            timeout=30,
        )
        log.append(checklist_copy.stdout + checklist_copy.stderr)
        if checklist_copy.returncode:
            raise RuntimeError("Die aktualisierte Testdokumentation konnte nicht in das persistente Volume übernommen werden.")
        write_state(status="success", branch=branch, started_at=started, finished_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), message=f"Update auf {branch} erfolgreich.", log="\n".join(log)[-16000:])
        if environment_backup:
            try:
                environment_backup.unlink(missing_ok=True)
            except OSError:
                pass
        remove_rollback_image(previous_image)
    except Exception as exc:
        log.append(str(exc))
        if environment_backup and environment_backup.exists():
            try:
                with (APP_DIR / ".env").open("w", encoding="utf-8") as target:
                    target.write(environment_backup.read_text(encoding="utf-8"))
                    target.flush()
                    os.fsync(target.fileno())
                environment_backup.unlink(missing_ok=True)
            except Exception as restore_exc:
                log.append("Wiederherstellung der .env fehlgeschlagen: " + str(restore_exc))
        rollback_message = ""
        if previous_image:
            try:
                rollback = compose("up", "-d", "--no-deps", "app", image=previous_image, timeout=240)
                log.append(rollback.stdout + rollback.stderr)
                rollback_message = " Vorheriges Image wurde wiederhergestellt." if rollback.returncode == 0 else " Wiederherstellung des vorherigen Images fehlgeschlagen."
                if rollback.returncode == 0:
                    remove_rollback_image(previous_image)
            except Exception as rollback_exc:
                log.append("Rollback: " + str(rollback_exc))
                rollback_message = " Wiederherstellung des vorherigen Images fehlgeschlagen."
        write_state(status="error", branch=branch, started_at=started, finished_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), message=str(exc) + rollback_message, log="\n".join(log)[-16000:])


class Handler(BaseHTTPRequestHandler):
    server_version = "MeetingManagerUpdater/1"

    def respond(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/status":
            return self.respond(200, read_state())
        if self.path == "/branches":
            try:
                return self.respond(200, {"branches": available_branches()})
            except (OSError, subprocess.SubprocessError, RuntimeError) as exc:
                return self.respond(503, {"error": str(exc)})
        if self.path == "/info":
            result = compose("ps", "-q", "app", timeout=30)
            if result.returncode or not result.stdout.strip():
                return self.respond(503, {"error": "App-Container ist nicht verfügbar."})
            container_id = result.stdout.strip().splitlines()[0]
            inspect = subprocess.run(
                ["/usr/bin/docker", "inspect", container_id],
                text=True, capture_output=True, timeout=30, check=False,
            )
            if inspect.returncode:
                return self.respond(503, {"error": "Image-Informationen sind nicht verfügbar."})
            details = json.loads(inspect.stdout)[0]
            labels = details.get("Config", {}).get("Labels") or {}
            image = details.get("Config", {}).get("Image", "")
            self.respond(200, {
                "branch": "main" if image.endswith(":latest") else "beta",
                "commit": labels.get("org.opencontainers.image.revision", ""),
                "version": labels.get("org.opencontainers.image.version", ""),
                "image": image,
                "created": details.get("Created", ""),
            })
            return
        return self.respond(404, {"error": "Nicht gefunden."})

    def do_POST(self):
        if self.path != "/update":
            return self.respond(404, {"error": "Nicht gefunden."})
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length < 1 or length > 1024:
                return self.respond(400, {"error": "Ungültige Anfragegröße."})
            payload = json.loads(self.rfile.read(length))
        except (ValueError, json.JSONDecodeError):
            return self.respond(400, {"error": "Ungültiges JSON."})
        branch = payload.get("branch") if isinstance(payload, dict) else None
        if not isinstance(branch, str) or not BRANCH_PATTERN.fullmatch(branch) or ".." in branch or branch.endswith(("/", ".")):
            return self.respond(400, {"error": "Ungültiger Branch-Name."})
        try:
            if branch not in available_branches():
                return self.respond(400, {"error": "Der ausgewählte Branch ist nicht mehr verfügbar."})
        except (OSError, subprocess.SubprocessError, RuntimeError) as exc:
            return self.respond(503, {"error": str(exc)})
        if not UPDATE_LOCK.acquire(blocking=False):
            return self.respond(409, {"error": "Ein Update läuft bereits."})
        state = read_state()
        if state.get("status") == "running":
            UPDATE_LOCK.release()
            return self.respond(409, {"error": "Ein Update läuft bereits."})

        started = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        write_state(status="running", branch=branch, started_at=started, finished_at=None, message="Update wird ausgeführt.", log="")

        def worker():
            try:
                run_update(branch)
            finally:
                UPDATE_LOCK.release()

        threading.Thread(target=worker, daemon=True).start()
        self.respond(202, {"status": "running", "branch": branch})

    def log_message(self, fmt, *args):
        # Requests and update outcomes are recorded in the system journal.
        print("%s - %s" % (self.address_string(), fmt % args), flush=True)


class ThreadedUnixServer(ThreadingMixIn, UnixStreamServer):
    daemon_threads = True


if __name__ == "__main__":
    recover_environment_backup()
    previous_state = read_state()
    if previous_state.get("status") == "running":
        write_state(
            status="error",
            finished_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            message="Der Docker-Updater wurde neu gestartet; der vorherige Lauf wurde unterbrochen.",
            log=(previous_state.get("log", "") + "\\nUpdater-Neustart erkannt.").strip(),
        )
    socket_path = "/run/meeting-manager-updater/control.sock"
    if os.path.exists(socket_path):
        os.unlink(socket_path)
    with ThreadedUnixServer(socket_path, Handler) as server:
        os.chown(socket_path, 0, grp.getgrnam('meeting-update').gr_gid)
        os.chmod(socket_path, 0o660)
        server.serve_forever()
