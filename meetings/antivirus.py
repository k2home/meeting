import socket
import struct

from django.conf import settings
from django.core.exceptions import ValidationError


def scan_uploaded_file(uploaded_file):
    """Scan an upload with ClamAV INSTREAM; fail closed when enabled but unavailable."""
    if not getattr(settings, "CLAMD_ENABLED", False) or not uploaded_file:
        return

    response = bytearray()
    try:
        uploaded_file.seek(0)
        with socket.create_connection(
            (settings.CLAMD_HOST, settings.CLAMD_PORT), timeout=10
        ) as client:
            client.settimeout(30)
            client.sendall(b"zINSTREAM\0")
            for chunk in uploaded_file.chunks():
                if chunk:
                    client.sendall(struct.pack("!I", len(chunk)))
                    client.sendall(chunk)
            client.sendall(struct.pack("!I", 0))

            while not response.endswith(b"\0"):
                part = client.recv(4096)
                if not part:
                    raise OSError("ClamAV hat die Verbindung vor einer Antwort geschlossen.")
                response.extend(part)
                if len(response) > 4096:
                    raise OSError("ClamAV-Antwort ist unerwartet groß.")
    except (OSError, ValueError, socket.timeout) as exc:
        raise ValidationError(
            "Die Datei konnte nicht sicher geprüft werden, weil der Malware-Scanner "
            "nicht erreichbar ist. Bitte später erneut versuchen oder den IT-Support informieren."
        ) from exc
    finally:
        try:
            uploaded_file.seek(0)
        except (AttributeError, OSError, ValueError):
            pass

    result = bytes(response).rstrip(b"\0")
    if b" FOUND" in result:
        raise ValidationError(
            "Die Datei wurde als Schadsoftware erkannt und kann nicht hochgeladen werden."
        )
    if not result.endswith(b" OK"):
        raise ValidationError(
            "Der Malware-Scanner konnte die Datei nicht eindeutig freigeben. "
            "Der Upload wurde vorsorglich abgebrochen."
        )
