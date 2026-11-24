import io
from pathlib import PurePosixPath
import zipfile

from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.text import slugify

from .access import accessible_topics

MAX_TOPIC_ATTACHMENT_ARCHIVE_BYTES = 100 * 1024 * 1024


def _archive_filename(storage_name, used_names, attachment_id):
    name = PurePosixPath((storage_name or "").replace("\\", "/")).name
    if not name:
        name = f"anlage-{attachment_id}"
    stem, dot, suffix = name.rpartition(".")
    if not dot or not stem:
        stem, suffix = name, ""
    candidate = name
    counter = 2
    while candidate.casefold() in used_names:
        candidate = f"{stem} ({counter})" + (f".{suffix}" if suffix else "")
        counter += 1
    used_names.add(candidate.casefold())
    return candidate


@login_required
def download_topic_attachments_zip(request, pk):
    """Download all uploaded files for a topic the current user may access."""
    topic = get_object_or_404(
        accessible_topics(request.user).prefetch_related("attachments"),
        pk=pk,
    )
    attachments = [
        item for item in topic.attachments.all()
        if item.uploaded_file
    ]
    if not attachments:
        raise Http404("Für dieses Thema sind keine hochgeladenen Dateien vorhanden.")

    total_size = sum(item.uploaded_file.size for item in attachments)
    if total_size > MAX_TOPIC_ATTACHMENT_ARCHIVE_BYTES:
        return HttpResponse(
            "Die Anlagen sind zusammen größer als das erlaubte ZIP-Exportlimit von 100 MB.",
            status=413,
            content_type="text/plain; charset=utf-8",
        )

    output = io.BytesIO()
    used_names = set()
    try:
        with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for attachment in attachments:
                filename = _archive_filename(
                    attachment.uploaded_file.name, used_names, attachment.pk
                )
                with attachment.uploaded_file.open("rb") as uploaded:
                    archive.writestr(filename, uploaded.read())
    except OSError as exc:
        raise Http404("Mindestens eine Anlage konnte nicht gelesen werden.") from exc

    filename = slugify(topic.title) or f"thema-{topic.pk}"
    response = HttpResponse(output.getvalue(), content_type="application/zip")
    response["Content-Disposition"] = f'attachment; filename="anlagen-{filename}.zip"'
    response["X-Content-Type-Options"] = "nosniff"
    response["Cache-Control"] = "private, no-store"
    return response
