#!/usr/bin/env python3
"""Restricted Docker Compose updater exposed only through a Unix socket."""
import json
import os
import grp
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
ALLOWED_BRANCHES = {"beta", "main"}


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
        subprocess.run(
            ["/usr/bin/docker", "image", "rm", image_ref],
            text=True, capture_output=True, timeout=30, check=False,
        )
def run_update(branch):
    started = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    write_state(status="running", branch=branch, started_at=started, finished_at=None, message="Update wird ausgeführt.", log="")
    log = []
    previous_image = None
    try:
        previous_image = preserve_running_image()
        target_image = f"ghcr.io/k2home/meeting:{'latest' if branch == 'main' else 'beta'}"
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
        write_state(status="success", branch=branch, started_at=started, finished_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), message=f"Update auf {branch} erfolgreich.", log="\n".join(log)[-16000:])
        remove_rollback_image(previous_image)
    except Exception as exc:
        log.append(str(exc))
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
        if branch not in ALLOWED_BRANCHES:
            return self.respond(400, {"error": "Erlaubt sind ausschließlich beta und main."})
        if not UPDATE_LOCK.acquire(blocking=False):
            return self.respond(409, {"error": "Ein Update läuft bereits."})
        state = read_state()
        if state.get("status") == "running":
            UPDATE_LOCK.release()
            return self.respond(409, {"error": "Ein Update läuft bereits."})

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
    socket_path = "/run/meeting-manager-updater/control.sock"
    if os.path.exists(socket_path):
        os.unlink(socket_path)
    with ThreadedUnixServer(socket_path, Handler) as server:
        os.chown(socket_path, 0, grp.getgrnam('meeting-update').gr_gid)
        os.chmod(socket_path, 0o660)
        server.serve_forever()
