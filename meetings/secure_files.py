from pathlib import Path

from django.conf import settings
from django.core.exceptions import SuspiciousFileOperation
from django.http import FileResponse, Http404
from django.utils._os import safe_join


def serve_topic_upload(attachment):
    """Stream an uploaded attachment after the calling view has checked login and ownership."""
    if not attachment.uploaded_file:
        raise Http404("Für diesen Eintrag ist keine Datei hochgeladen.")

    try:
        root = Path(settings.MEDIA_ROOT).resolve(strict=True)
        path = Path(safe_join(str(root), attachment.uploaded_file.name)).resolve(strict=True)
        path.relative_to(root)
    except (FileNotFoundError, ValueError, SuspiciousFileOperation):
        raise Http404("Die Datei wurde nicht gefunden.")

    if not path.is_file():
        raise Http404("Die Datei wurde nicht gefunden.")

    response = FileResponse(path.open("rb"), as_attachment=True, filename=path.name)
    response["X-Content-Type-Options"] = "nosniff"
    response["Cache-Control"] = "private, no-store"
    return response
