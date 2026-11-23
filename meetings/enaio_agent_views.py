import hashlib
import json
import secrets
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.db import transaction, models
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .models import EnaioAgent, EnaioFolderSelection, EnaioSettings, EnaioTransfer


def _digest(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _agent_from_request(request):
    header = request.headers.get("Authorization", "")
    if not header.startswith("Bearer "):
        return None
    digest = _digest(header[7:].strip())
    agent = EnaioAgent.objects.select_related("user").filter(device_token_hash=digest).first()
    if agent and agent.user.is_active:
        EnaioAgent.objects.filter(pk=agent.pk).update(last_seen_at=timezone.now())
        return agent
    return None


@login_required
@require_http_methods(["POST"])
def enaio_agent_pair_code(request):
    code = secrets.token_urlsafe(9)
    agent, _ = EnaioAgent.objects.get_or_create(user=request.user)
    agent.pairing_code_hash = _digest(code)
    agent.pairing_expires_at = timezone.now() + timedelta(minutes=10)
    agent.save(update_fields=["pairing_code_hash", "pairing_expires_at", "updated_at"])
    return JsonResponse({"pairing_code": code, "expires_in": 600})


@csrf_exempt
@require_http_methods(["POST"])
def enaio_agent_register(request):
    try:
        data = json.loads(request.body or b"{}")
    except (ValueError, UnicodeDecodeError):
        return JsonResponse({"error": "Ungültige JSON-Daten."}, status=400)
    code = str(data.get("pairing_code", "")).strip()
    if not code:
        return JsonResponse({"error": "Kopplungscode fehlt."}, status=400)
    digest = _digest(code)
    agent = EnaioAgent.objects.filter(
        pairing_code_hash=digest, pairing_expires_at__gt=timezone.now(),
        user__is_active=True,
    ).select_related("user").first()
    if not agent:
        return JsonResponse({"error": "Kopplungscode ungültig oder abgelaufen."}, status=403)
    token = secrets.token_urlsafe(48)
    agent.device_token_hash = _digest(token)
    agent.pairing_code_hash = ""
    agent.pairing_expires_at = None
    agent.device_name = str(data.get("device_name", "Windows-PC"))[:120]
    agent.save(update_fields=["device_token_hash", "pairing_code_hash", "pairing_expires_at", "device_name", "updated_at"])
    return JsonResponse({"device_token": token, "poll_interval_seconds": 5})


@require_http_methods(["GET"])
def enaio_agent_next_job(request):
    agent = _agent_from_request(request)
    if not agent:
        return HttpResponseForbidden("Agent nicht authentifiziert.")
    now = timezone.now()
    with transaction.atomic():
        selection = EnaioFolderSelection.objects.select_for_update().filter(
            user=agent.user, consumed_at__isnull=True, expires_at__gt=now,
        ).filter(
            models.Q(agent_lease_token="") | models.Q(agent_lease_expires_at__isnull=True) |
            models.Q(agent_lease_expires_at__lte=now)
        ).order_by("created_at").first()
        transfer = EnaioTransfer.objects.select_for_update().filter(
            user=agent.user, status="pending", consumed_at__isnull=True, expires_at__gt=now,
        ).filter(
            models.Q(agent_lease_token="") | models.Q(agent_lease_expires_at__isnull=True) |
            models.Q(agent_lease_expires_at__lte=now)
        ).order_by("created_at").first()

        if selection and (not transfer or selection.created_at <= transfer.created_at):
            lease = secrets.token_urlsafe(32)
            selection.agent_lease_token = lease
            selection.agent_lease_expires_at = min(selection.expires_at, now + timedelta(minutes=10))
            selection.save(update_fields=["agent_lease_token", "agent_lease_expires_at"])
            data = {"job": {
                "id": f"folder-{selection.pk}", "kind": "select_root_folder",
                "selection_id": selection.pk, "lease_token": lease,
                "complete_url": request.build_absolute_uri(f"/enaio/agent/selection/{selection.pk}/complete/"),
                "fail_url": request.build_absolute_uri(f"/enaio/agent/jobs/selection/{selection.pk}/fail/"),
            }}
        elif transfer:
            settings_obj = EnaioSettings.objects.filter(pk=1).first()
            if not settings_obj or not settings_obj.root_folder_id:
                data = {"job": None, "configuration_error": "Der zentrale enaio-Stammordner ist nicht konfiguriert."}
                response = JsonResponse(data, status=409)
                response["Cache-Control"] = "no-store"
                return response
            lease = secrets.token_urlsafe(32)
            transfer.agent_lease_token = lease
            transfer.agent_lease_expires_at = min(transfer.expires_at, now + timedelta(minutes=10))
            transfer.save(update_fields=["agent_lease_token", "agent_lease_expires_at"])
            from .views import _meeting_series_name
            data = {"job": {
                "id": f"transfer-{transfer.pk}", "kind": "file_protocol",
                "transfer_id": transfer.pk, "lease_token": lease,
                "filing": {
                    "root_folder_id": settings_obj.root_folder_id,
                    "root_folder_type": settings_obj.root_folder_type,
                    "root_folder_name": settings_obj.root_folder_name,
                    "root_folder_path": settings_obj.root_folder_path,
                    "register_name": _meeting_series_name(transfer.meeting),
                    "archive_name": settings_obj.archive_name,
                    "register_type_name": settings_obj.register_type_name,
                    "register_name_field": settings_obj.register_name_field,
                    "document_type": "Standard",
                },
                "pdf_url": request.build_absolute_uri(f"/enaio/agent/transfer/{transfer.pk}/pdf/"),
                "complete_url": request.build_absolute_uri(f"/enaio/agent/transfer/{transfer.pk}/complete/"),
                "fail_url": request.build_absolute_uri(f"/enaio/agent/jobs/transfer/{transfer.pk}/fail/"),
            }}
        else:
            data = {"job": None}
    response = JsonResponse(data)
    response["Cache-Control"] = "no-store"
    return response

@csrf_exempt
@require_http_methods(["POST"])
def enaio_agent_selection_complete(request, pk):
    agent = _agent_from_request(request)
    if not agent:
        return HttpResponseForbidden("Agent nicht authentifiziert.")
    try:
        data = json.loads(request.body or b"{}")
        lease_token = str(data.get("lease_token", ""))
        folder_id = str(data.get("folder_id", "")).strip()
        folder_name = str(data.get("folder_name", "")).strip()
        folder_path = str(data.get("folder_path", "")).strip()
        folder_type = int(data.get("folder_type", 0))
    except (ValueError, TypeError, UnicodeDecodeError):
        return JsonResponse({"error": "Ungültige enaio-Auswahldaten."}, status=400)
    if not folder_id or len(folder_id) > 64 or not folder_name or len(folder_name) > 255 or len(folder_path) > 1000 or folder_type < 0:
        return JsonResponse({"error": "Ordner-ID, Name, Pfad oder Objekttyp ungültig."}, status=400)
    with transaction.atomic():
        selection = EnaioFolderSelection.objects.select_for_update().filter(
            pk=pk, user=agent.user, consumed_at__isnull=True, expires_at__gt=timezone.now(),
            agent_lease_token=lease_token, agent_lease_expires_at__gt=timezone.now()
        ).first()
        if not selection:
            return HttpResponseForbidden("Auswahlauftrag ungültig oder bereits verwendet.")
        settings_obj, _ = EnaioSettings.objects.get_or_create(pk=1)
        settings_obj.root_folder_id = folder_id
        settings_obj.root_folder_type = folder_type
        settings_obj.root_folder_name = folder_name
        settings_obj.root_folder_path = folder_path
        settings_obj.save()
        selection.selected_folder_id = folder_id
        selection.selected_folder_type = folder_type
        selection.selected_folder_name = folder_name
        selection.selected_folder_path = folder_path
        selection.consumed_at = timezone.now()
        selection.save(update_fields=["selected_folder_id", "selected_folder_type", "selected_folder_name", "selected_folder_path", "consumed_at"])
    return JsonResponse({"ok": True})


@require_http_methods(["GET"])
def enaio_agent_transfer_pdf(request, pk):
    agent = _agent_from_request(request)
    if not agent:
        return HttpResponseForbidden("Agent nicht authentifiziert.")
    transfer = get_object_or_404(EnaioTransfer, pk=pk, user=agent.user, status="pending", consumed_at__isnull=True, expires_at__gt=timezone.now())
    from .views import protocol_pdf
    request.user = agent.user
    return protocol_pdf(request, transfer.meeting_id)


@csrf_exempt
@require_http_methods(["POST"])
def enaio_agent_transfer_complete(request, pk):
    agent = _agent_from_request(request)
    if not agent:
        return HttpResponseForbidden("Agent nicht authentifiziert.")
    try:
        data = json.loads(request.body or b"{}")
        lease_token = str(data.get("lease_token", ""))
        uploaded = data.get("uploaded") is True
        object_id = str(data.get("object_id", "")).strip()
        display_path = str(data.get("display_path", "")).strip()
        object_type = int(data.get("object_type", 0))
    except (ValueError, TypeError, UnicodeDecodeError):
        return JsonResponse({"error": "Ungültige Rückmeldung."}, status=400)
    if not uploaded or not object_id or len(object_id) > 64 or not display_path or len(display_path) > 1000 or object_type < 0:
        return JsonResponse({"error": "Ablage nicht erfolgreich bestätigt oder Rückmeldedaten ungültig."}, status=400)
    with transaction.atomic():
        transfer = EnaioTransfer.objects.select_for_update().filter(
            pk=pk, user=agent.user, status="pending", consumed_at__isnull=True, expires_at__gt=timezone.now(),
            agent_lease_token=lease_token, agent_lease_expires_at__gt=timezone.now()
        ).first()
        if not transfer:
            return HttpResponseForbidden("Ablageauftrag ungültig oder bereits verwendet.")
        transfer.status = "completed"
        transfer.consumed_at = timezone.now()
        transfer.save(update_fields=["status", "consumed_at"])
    return JsonResponse({"ok": True, "register_path": display_path})



@csrf_exempt
@require_http_methods(["POST"])
def enaio_agent_job_fail(request, kind, pk):
    agent = _agent_from_request(request)
    if not agent:
        return HttpResponseForbidden("Agent nicht authentifiziert.")
    try:
        data = json.loads(request.body or b"{}")
        lease_token = str(data.get("lease_token", ""))
        message = str(data.get("error", "enaio-Auftrag fehlgeschlagen.")).strip()[:500]
    except (ValueError, TypeError, UnicodeDecodeError):
        return JsonResponse({"error": "Ungültige Fehlerrückmeldung."}, status=400)
    now = timezone.now()
    with transaction.atomic():
        if kind == "selection":
            job = EnaioFolderSelection.objects.select_for_update().filter(
                pk=pk, user=agent.user, consumed_at__isnull=True,
                agent_lease_token=lease_token, agent_lease_expires_at__gt=now,
            ).first()
            if not job:
                return HttpResponseForbidden("Auftrag ungültig oder Lease abgelaufen.")
            job.error_message = message
            job.consumed_at = now
            job.save(update_fields=["error_message", "consumed_at"])
        elif kind == "transfer":
            job = EnaioTransfer.objects.select_for_update().filter(
                pk=pk, user=agent.user, status="pending", consumed_at__isnull=True,
                agent_lease_token=lease_token, agent_lease_expires_at__gt=now,
            ).first()
            if not job:
                return HttpResponseForbidden("Auftrag ungültig oder Lease abgelaufen.")
            job.status = "failed"
            job.error_message = message
            job.consumed_at = now
            job.save(update_fields=["status", "error_message", "consumed_at"])
        else:
            return JsonResponse({"error": "Unbekannter Auftragstyp."}, status=404)
    return JsonResponse({"ok": True})
