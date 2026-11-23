from zoneinfo import available_timezones
import logging
from datetime import timedelta
import os
import json
import subprocess
import tempfile
import zipfile
from pathlib import Path

from django.core.management import call_command
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.db.migrations.loader import MigrationLoader
from django.db.migrations.recorder import MigrationRecorder

from django import forms
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import password_validation
from django.core.mail import send_mail
from django.conf import settings
from django.http import FileResponse, HttpResponse, JsonResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from .access import is_admin
from .models import MeetingSeries, OrganizationSettings, SeriesAccess, UserProfile, EnaioSettings, EnaioFolderSelection, EnaioDiagnosticReport, EnaioAgentLog
from .user_csv import export_users_csv, import_users_csv
from .topic_csv import export_topic_agenda_csv, import_topic_agenda_csv, sample_csv_response
from .user_display import user_display_name_with_login
from .user_roles import sync_admin_access

logger = logging.getLogger(__name__)

User = get_user_model()


def _require_admin(request):
    if not is_admin(request.user):
        raise PermissionDenied


class ManagedUserCreateForm(UserCreationForm):
    first_name = forms.CharField(label="Vorname", max_length=150, required=False)
    last_name = forms.CharField(label="Nachname", max_length=150, required=False)
    email = forms.EmailField(label="E-Mail-Adresse", required=False)
    short_description = forms.CharField(label="Kurzbeschreibung", max_length=80, required=False)
    is_administrator = forms.BooleanField(label="Administrator", required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "last_name", "email")

    def save(self, commit=True):
        user = super().save(commit=False)
        for field in ("first_name", "last_name", "email"):
            setattr(user, field, self.cleaned_data.get(field, "").strip())
        if commit:
            user.save()
            UserProfile.objects.update_or_create(
                user=user, defaults={"short_description": self.cleaned_data.get("short_description", "").strip()}
            )
            sync_admin_access(user, self.cleaned_data.get("is_administrator", False))
        return user


class ManagedUserEditForm(forms.ModelForm):
    short_description = forms.CharField(label="Kurzbeschreibung", max_length=80, required=False)
    is_administrator = forms.BooleanField(label="Administrator", required=False)

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "is_active")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].disabled = True
        profile = getattr(self.instance, "meeting_profile", None) if self.instance.pk else None
        self.fields["short_description"].initial = profile.short_description if profile else ""
        self.fields["last_login"] = forms.CharField(label="Letzte Anmeldung", required=False, disabled=True, initial=self.instance.last_login.strftime("%d.%m.%Y, %H:%M") if self.instance.last_login else "Noch nie")
        self.fields["date_joined"] = forms.CharField(label="Erstellt am", required=False, disabled=True, initial=self.instance.date_joined.strftime("%d.%m.%Y, %H:%M") if self.instance.date_joined else "–")
        self.fields["is_administrator"].initial = (
            self.instance.groups.filter(name="Admin").exists() if self.instance.pk else False
        )

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            UserProfile.objects.update_or_create(
                user=user, defaults={"short_description": self.cleaned_data.get("short_description", "").strip()}
            )
            sync_admin_access(user, self.cleaned_data.get("is_administrator", False))
        return user


class OrganizationSettingsForm(forms.ModelForm):
    timezone = forms.ChoiceField(
        label="Zeitzone",
        choices=[(zone, zone) for zone in sorted(available_timezones())],
    )

    class Meta:
        model = OrganizationSettings
        fields = (
            "name", "short_name", "timezone", "attachment_max_size_mb",
            "primary_color", "primary_color_light", "primary_color_dark",
            "secondary_color", "secondary_color_light", "secondary_color_dark",
            "tertiary_color", "tertiary_color_light", "tertiary_color_dark",
        )


class OrganizationLogoForm(forms.ModelForm):
    class Meta:
        model = OrganizationSettings
        fields = ("logo",)
        labels = {"logo": "Organisationslogo auswählen"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["logo"].widget.attrs.update({
            "accept": ".png,.jpg,.jpeg,.svg,image/png,image/jpeg,image/svg+xml",
        })


class EnaioSettingsForm(forms.Form):
    document_type_name = forms.CharField(label="Technischer Dokumenttyp", max_length=255, required=True, help_text="Dokumenttyp, der in enaio für das Protokoll-PDF verwendet wird (z. B. Standard).")
    root_folder_id = forms.CharField(label="enaio-Ordner-ID", max_length=64,
        help_text="ID des zentralen enaio-Ordners. Sie können die ID direkt eingeben oder über den enaio-Client auswählen.")
    root_folder_type = forms.IntegerField(label="enaio-Objekttyp", min_value=0, required=False, initial=0,
        help_text="Wird bei einer Auswahl im enaio-Client automatisch übernommen. Bei manueller Eingabe normalerweise 0 belassen.")


@login_required
def management_enaio_settings(request):
    _require_admin(request)
    instance = EnaioSettings.objects.filter(pk=1).first()
    initial = {
        "document_type_name": instance.document_type_name if instance else "Standard",
        "root_folder_id": instance.root_folder_id if instance else "",
        "root_folder_type": instance.root_folder_type if instance else 0,
    }
    form = EnaioSettingsForm(request.POST or None, initial=initial)
    if request.method == "POST" and form.is_valid():
        settings_obj, _ = EnaioSettings.objects.get_or_create(pk=1)
        new_folder_id = form.cleaned_data["root_folder_id"].strip()
        if settings_obj.root_folder_id != new_folder_id:
            settings_obj.root_folder_name = ""
            settings_obj.root_folder_path = ""
        settings_obj.document_type_name = form.cleaned_data["document_type_name"].strip()
        settings_obj.root_folder_id = new_folder_id
        settings_obj.root_folder_type = form.cleaned_data.get("root_folder_type") or 0
        settings_obj.save()
        messages.success(request, "Die enaio-Einstellungen wurden gespeichert.")
        return redirect("management_enaio_settings")
    return render(request, "meetings/management_enaio_settings.html", {
        "form": form, "configured": bool(instance and instance.root_folder_id),
        "object_definition_configured": False,
        "object_definition_automatic": True,
        "folder_name": instance.root_folder_name if instance else "",
        "folder_path": instance.root_folder_path if instance else "",
    })



@login_required
@require_http_methods(["GET"])
def enaio_connection_diagnostics(request):
    """Return safe server-side facts for the browser-based enaio diagnostics."""
    _require_admin(request)
    config = EnaioSettings.objects.filter(pk=1).first()
    required_fields = [
        ("document_type_name", "Technischer Dokumenttyp"),
    ]
    missing_fields = [
        {"field": field, "label": label}
        for field, label in required_fields
        if not config or not (getattr(config, field, "") or "").strip()
    ]
    return JsonResponse({
        "server": {
            "authenticated_request": True,
            "https": request.is_secure(),
            "same_origin_api": True,
        },
        "configuration": {
            "root_folder_configured": bool(config and config.root_folder_id),
            # Object metadata will be read from the selected folder in the
            # already-running enaio client; it is intentionally not a
            # manually configured server-side setting.
            "object_definition_configured": False,
            "object_definition_automatic": True,
            "document_type_configured": bool(config and config.document_type_name),
            "missing_fields": missing_fields,
        },
        "checks_not_possible_from_server": [
            "COM-Zugriff auf den enaio-Prozess des Citrix-Benutzers",
            "Auslesen der aktiven enaio-Session-GUID",
            "Ermitteln der im enaio-Client geöffneten Ordner",
            "Erreichbarkeit lokaler Citrix-Prozesse aus dem Browser",
        ],
        "note": "Der Server kann die lokale Windows-/Citrix-Sitzung des Browserbenutzers nicht einsehen.",
    })


def _redact_diagnostic_value(value):
    import re
    if isinstance(value, dict):
        return {str(key)[:100]: _redact_diagnostic_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_redact_diagnostic_value(item) for item in value[:500]]
    if isinstance(value, str):
        text = value[:12000]
        text = re.sub(r"(?i)(bearer\s+)[A-Za-z0-9._~+/-]+=*", r"\1[REDACTED]", text)
        text = re.sub(r"(?i)((?:password|passwd|secret|token|cookie|authorization|session(?:id|_id)?|pairing[_-]?code)\s*[:=]\s*)[^\s,;]+", r"\1[REDACTED]", text)
        return text
    if value is None or isinstance(value, (bool, int, float)):
        return value
    return str(value)[:1000]


def _analyze_enaio_report(report, logs):
    tests = [item for section in ("browser", "server") for item in report.get(section, []) if isinstance(item, dict)]
    errors = [item for item in tests if str(item.get("result", "")).upper() in {"FEHLER", "ERROR", "FAILED"}]
    warnings = [item for item in tests if any(word in str(item.get("result", "")).upper() for word in ("FEHLT", "UNVOLLSTÄNDIG", "NICHT VERFÜGBAR", "NICHT DIREKT VERFÜGBAR", "NICHT MÖGLICH", "HINWEIS"))]
    agent_errors = [item for item in logs if item["level"] == "ERROR"]
    agent_warnings = [item for item in logs if item["level"] == "WARNING"]
    local_lines = str(report.get("local_log_text", "")).splitlines()
    local_errors = [line for line in local_lines if any(word in line.upper() for word in (" ERROR ", "[ERROR]", "EXCEPTION", "TRACEBACK", "FATAL"))]
    local_warnings = [line for line in local_lines if any(word in line.upper() for word in (" WARNING ", "[WARN]", "[WARNING]"))]
    return {
        "browser_server_checks": len(tests),
        "diagnostic_errors": len(errors),
        "diagnostic_warnings": len(warnings),
        "agent_log_entries": len(logs),
        "agent_errors": len(agent_errors),
        "agent_warnings": len(agent_warnings),
        "local_log_lines": len(local_lines),
        "local_log_errors": len(local_errors),
        "local_log_warnings": len(local_warnings),
        "local_log_findings": (local_errors + local_warnings)[:100],
        "findings": [{"test": item.get("test", "Unbekannter Test"), "result": item.get("result", ""), "detail": item.get("detail", "")} for item in errors + warnings],
        "recommendation": "Fehler in den lokalen oder übertragenen Agent-Logs zuerst prüfen." if agent_errors or local_errors else "Die erkannten Konfigurations- und Integrationshinweise prüfen." if warnings or local_warnings else "Keine auffälligen Diagnoseergebnisse erkannt.",
    }


@login_required
@require_http_methods(["POST"])
def enaio_diagnostic_report_save(request):
    _require_admin(request)
    import json
    if len(request.body) > 150000:
        return JsonResponse({"error": "Der Diagnosebericht ist zu groß."}, status=413)
    try:
        payload = json.loads(request.body or b"{}")
    except (ValueError, UnicodeDecodeError):
        return JsonResponse({"error": "Ungültiger JSON-Bericht."}, status=400)
    if not isinstance(payload, dict) or payload.get("report_type") != "Meeting Manager – enaio Browserdiagnose":
        return JsonResponse({"error": "Unbekanntes Berichtsformat."}, status=400)
    if len(str(payload.get("local_log_text", ""))) > 100000:
        return JsonResponse({"error": "Die lokale Logdatei überschreitet 100 KB."}, status=413)
    safe_report = _redact_diagnostic_value(payload)
    logs = [{
        "created_at": item.created_at.isoformat(), "level": item.level,
        "device": item.agent.device_name or "Unbekannter Arbeitsplatz",
        "user": item.agent.user.get_full_name() or item.agent.user.get_username(),
        "message": _redact_diagnostic_value(item.message),
    } for item in EnaioAgentLog.objects.select_related("agent", "agent__user").order_by("-created_at")[:300]]
    safe_report["agent_logs"] = logs
    analysis = _analyze_enaio_report(safe_report, logs)
    saved = EnaioDiagnosticReport.objects.create(created_by=request.user, report=safe_report, analysis=analysis)
    old_ids = list(EnaioDiagnosticReport.objects.order_by("-created_at", "-pk").values_list("pk", flat=True)[20:])
    if old_ids:
        EnaioDiagnosticReport.objects.filter(pk__in=old_ids).delete()
    return JsonResponse({"id": saved.pk, "created_at": saved.created_at.isoformat(), "report": saved.report, "analysis": saved.analysis})


@login_required
@require_http_methods(["GET"])
def enaio_diagnostic_report_latest(request):
    _require_admin(request)
    saved = EnaioDiagnosticReport.objects.first()
    if not saved:
        return JsonResponse({"available": False})
    return JsonResponse({"available": True, "id": saved.pk, "created_at": saved.created_at.isoformat(), "report": saved.report, "analysis": saved.analysis})


@login_required
@require_http_methods(["POST"])
def enaio_folder_selection_start(request):
    _require_admin(request)
    selection = EnaioFolderSelection.objects.create(
        user=request.user,
        expires_at=timezone.now() + timedelta(minutes=5),
    )
    return JsonResponse({
        "status_url": reverse("enaio_folder_selection_status", args=[selection.pk]),
        "cancel_url": reverse("enaio_folder_selection_cancel", args=[selection.pk]),
        "message": "Der lokale enaio-Agent übernimmt die Ordnerauswahl.",
        "expires_in": 300,
    })


@login_required
@require_http_methods(["GET"])
def enaio_folder_selection_status(request, pk):
    _require_admin(request)
    selection = get_object_or_404(EnaioFolderSelection, pk=pk, user=request.user)
    if selection.error_message:
        return JsonResponse({"completed": False, "error": selection.error_message}, status=400)
    if selection.consumed_at:
        return JsonResponse({"completed": True})
    if selection.expires_at <= timezone.now():
        EnaioFolderSelection.objects.filter(pk=selection.pk, consumed_at__isnull=True).update(
            consumed_at=timezone.now(), error_message="Die Ordnerauswahl ist abgelaufen."
        )
        return JsonResponse({"completed": False, "expired": True}, status=410)
    return JsonResponse({"completed": False})


@login_required
@require_http_methods(["POST"])
def enaio_folder_selection_cancel(request, pk):
    _require_admin(request)
    with transaction.atomic():
        selection = EnaioFolderSelection.objects.select_for_update().filter(pk=pk, user=request.user).first()
        if not selection:
            return JsonResponse({"error": "Ordnerauswahl nicht gefunden."}, status=404)
        if selection.consumed_at is None:
            selection.error_message = "Die Ordnerauswahl wurde vom Benutzer abgebrochen."
            selection.consumed_at = timezone.now()
            selection.save(update_fields=["error_message", "consumed_at"])
    return JsonResponse({"ok": True})


@login_required
def management_home(request):
    _require_admin(request)
    return render(request, "meetings/management.html", {
        "user_count": User.objects.count(),
        "active_user_count": User.objects.filter(is_active=True).count(),
        "series_count": MeetingSeries.objects.count(),
    })


@login_required
def management_users(request):
    _require_admin(request)
    users = User.objects.all().order_by("last_name", "first_name", "username")
    return render(request, "meetings/management_users.html", {
        "users": [{"account": user, "is_administrator": is_admin(user)} for user in users],
        "role_choices": SeriesAccess.ROLE_CHOICES,
    })


@login_required
def management_user_edit(request, pk=None):
    _require_admin(request)
    instance = get_object_or_404(User, pk=pk) if pk else None
    if instance:
        form = ManagedUserEditForm(request.POST or None, instance=instance)
    else:
        form = ManagedUserCreateForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        if instance and instance.pk == request.user.pk and not form.cleaned_data["is_active"]:
            form.add_error("is_active", "Das eigene Administratorkonto kann hier nicht deaktiviert werden.")
        else:
            with transaction.atomic():
                user = form.save()
            messages.success(request, f"Benutzer „{user_display_name_with_login(user)}“ wurde gespeichert.")
            return redirect("management_users")
    return render(request, "meetings/management_user_form.html", {
        "form": form, "page_title": "Benutzer bearbeiten" if instance else "Benutzer hinzufügen",
        "is_new": instance is None,
    })


@login_required
def management_groups(request):
    _require_admin(request)
    if request.method == "POST":
        action = request.POST.get("action")
        try:
            with transaction.atomic():
                if action == "add":
                    series = get_object_or_404(MeetingSeries, pk=request.POST.get("series_id"))
                    user = get_object_or_404(User, pk=request.POST.get("user_id"))
                    role = request.POST.get("role")
                    if role not in dict(SeriesAccess.ROLE_CHOICES):
                        raise ValueError("Bitte eine gültige Berechtigung auswählen.")
                    access, created = SeriesAccess.objects.get_or_create(
                        series=series, user=user, defaults={"role": role}
                    )
                    if not created:
                        access.role = role
                        access.save(update_fields=["role"])
                    messages.success(request, f"{user_display_name_with_login(user)} wurde der Gruppe „{series.name}“ zugeordnet.")
                elif action == "update":
                    access = get_object_or_404(SeriesAccess.objects.select_related("series", "user"), pk=request.POST.get("access_id"))
                    role = request.POST.get("role")
                    if role not in dict(SeriesAccess.ROLE_CHOICES):
                        raise ValueError("Bitte eine gültige Berechtigung auswählen.")
                    access.role = role
                    access.save(update_fields=["role"])
                    messages.success(request, "Die Gruppenberechtigung wurde aktualisiert.")
                elif action == "remove":
                    access = get_object_or_404(SeriesAccess.objects.select_related("series", "user"), pk=request.POST.get("access_id"))
                    label = f"{user_display_name_with_login(access.user)} aus „{access.series.name}“"
                    access.delete()
                    messages.success(request, f"{label} wurde entfernt.")
                else:
                    raise ValueError("Unbekannte Aktion.")
        except ValueError as exc:
            messages.error(request, str(exc))
        return redirect("management_groups")

    access_qs = SeriesAccess.objects.select_related("series", "user").all()
    query = request.GET.get("q", "").strip()
    role_filter = request.GET.get("role", "")
    if query:
        from django.db.models import Q
        access_qs = access_qs.filter(Q(user__username__icontains=query) | Q(user__first_name__icontains=query) | Q(user__last_name__icontains=query) | Q(series__name__icontains=query))
    if role_filter in dict(SeriesAccess.ROLE_CHOICES):
        access_qs = access_qs.filter(role=role_filter)
    access_ids = set(access_qs.values_list("pk", flat=True))
    series_rows = [{
        "series": series,
        "members": [a for a in series.user_access.select_related("user").all() if a.pk in access_ids],
    } for series in MeetingSeries.objects.order_by("name")]
    series_rows = [row for row in series_rows if row["members"] or not (query or role_filter)]
    return render(request, "meetings/management_groups.html", {
        "series_rows": series_rows,
        "available_users": User.objects.order_by("last_name", "first_name", "username"),
        "search": request.GET.get("q", ""),
        "role_filter": request.GET.get("role", ""),
        "role_choices": SeriesAccess.ROLE_CHOICES,
    })


@login_required
def management_settings(request):
    _require_admin(request)
    instance = OrganizationSettings.objects.filter(pk=1).first() or OrganizationSettings()
    logo_form = OrganizationLogoForm(instance=instance)
    form = OrganizationSettingsForm(instance=instance)

    if request.method == "POST" and request.POST.get("action") == "save_logo":
        logo_form = OrganizationLogoForm(request.POST, request.FILES, instance=instance)
        if logo_form.is_valid():
            settings_obj = logo_form.save(commit=False)
            settings_obj.full_clean()
            settings_obj.save()
            uploaded_logo = settings_obj.logo
            if uploaded_logo and uploaded_logo.name.lower().endswith(".svg"):
                previous_png_name = settings_obj.logo_png.name if settings_obj.logo_png else ""
                try:
                    import cairosvg
                    from django.core.files.base import ContentFile
                    uploaded_logo.open("rb")
                    try:
                        svg_data = uploaded_logo.read()
                    finally:
                        uploaded_logo.close()
                    png_data = cairosvg.svg2png(
                        bytestring=svg_data, output_width=1600,
                        background_color="#ffffff",
                    )
                    png_name = uploaded_logo.name.rsplit("/", 1)[-1].rsplit(".", 1)[0] + ".png"
                    settings_obj.logo_png.save(png_name, ContentFile(png_data), save=True)
                    if previous_png_name and previous_png_name != settings_obj.logo_png.name:
                        settings_obj.logo.storage.delete(previous_png_name)
                except Exception:
                    logger.exception("Organisationslogo-SVG konnte beim Speichern nicht in PNG konvertiert werden.")
                    if settings_obj.logo_png:
                        settings_obj.logo_png.delete(save=False)
                        settings_obj.save(update_fields=["logo_png"])
                    logo_form.add_error("logo", "Die SVG-Datei konnte nicht in eine PNG-Datei konvertiert werden. Bitte prüfen Sie die Datei oder laden Sie eine PNG-Version hoch.")
                    return render(request, "meetings/management_settings.html", {
                        "form": form, "logo_form": logo_form, "organization_settings": instance,
                    })
            else:
                if settings_obj.logo_png:
                    settings_obj.logo_png.delete(save=False)
                    settings_obj.save(update_fields=["logo_png"])
            messages.success(request, "Das Organisationslogo wurde gespeichert und für den PDF-Export vorbereitet.")
            return redirect("management_settings")
    elif request.method == "POST":
        form = OrganizationSettingsForm(request.POST, instance=instance)
        if form.is_valid():
            settings_obj = form.save(commit=False)
            settings_obj.full_clean()
            settings_obj.save()
            messages.success(request, "Die Organisationseinstellungen wurden gespeichert.")
            return redirect("management_settings")

    return render(request, "meetings/management_settings.html", {
        "form": form, "logo_form": logo_form, "organization_settings": instance,
    })


DATABASE_BACKUP_MAX_BYTES = 1024 * 1024 * 1024  # 1 GiB
DATABASE_BACKUP_FORMAT_VERSION = 1


def _database_client_environment():
    database = settings.DATABASES["default"]
    if database.get("ENGINE") != "django.db.backends.postgresql":
        raise RuntimeError("Der vollständige Datenbankexport wird derzeit nur für PostgreSQL unterstützt.")
    env = os.environ.copy()
    env.update({
        "PGHOST": str(database.get("HOST") or ""),
        "PGPORT": str(database.get("PORT") or "5432"),
        "PGUSER": str(database.get("USER") or ""),
        "PGPASSWORD": str(database.get("PASSWORD") or ""),
    })
    return env, str(database["NAME"])


def _run_database_client(command, env, timeout=1800):
    return subprocess.run(
        command, env=env, stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        timeout=timeout, check=False,
    )


def _database_schema_migrations():
    return [
        {"app": app_label, "name": migration_name}
        for app_label, migration_name in sorted(MigrationRecorder(connection).applied_migrations())
    ]


def _validate_backup_migrations(migrations):
    if not isinstance(migrations, list):
        raise RuntimeError("Die Sicherung enthält keine gültige Django-Migrationshistorie.")
    normalized = set()
    for item in migrations:
        if not isinstance(item, dict):
            raise RuntimeError("Die Migrationshistorie der Sicherung ist beschädigt.")
        app_label, name = item.get("app"), item.get("name")
        if not isinstance(app_label, str) or not app_label or not isinstance(name, str) or not name:
            raise RuntimeError("Die Migrationshistorie der Sicherung ist beschädigt.")
        key = (app_label, name)
        if key in normalized:
            raise RuntimeError("Die Migrationshistorie der Sicherung enthält doppelte Einträge.")
        normalized.add(key)

    current_migrations = MigrationLoader(None).graph.nodes
    unknown = sorted(normalized.difference(current_migrations))
    if unknown:
        details = ", ".join(f"{app}.{name}" for app, name in unknown[:10])
        raise RuntimeError(
            "Dieses Backup stammt aus einer neueren oder inkompatiblen Datenbankversion. "
            f"Die benötigten Migrationen sind im aktuellen Programm nicht vorhanden: {details}"
        )
    return normalized


def _restore_database_dump(dump_path, database_name, env):
    # pg_restore --clean only removes objects present in the archive. Remove all
    # application schemas first so tables introduced after an older backup do
    # not survive and collide with forward migrations.
    clear_schemas_sql = """
DO $meeting_manager$
DECLARE
    schema_record record;
BEGIN
    FOR schema_record IN
        SELECT nspname
        FROM pg_namespace
        WHERE nspname <> 'information_schema'
          AND nspname !~ '^pg_'
    LOOP
        EXECUTE format('DROP SCHEMA %I CASCADE', schema_record.nspname);
    END LOOP;
    EXECUTE 'CREATE SCHEMA public AUTHORIZATION CURRENT_USER';
    EXECUTE 'GRANT ALL ON SCHEMA public TO CURRENT_USER';
    EXECUTE 'GRANT USAGE ON SCHEMA public TO PUBLIC';
END
$meeting_manager$;
"""
    cleared = _run_database_client(
        ["psql", "--set", "ON_ERROR_STOP=1", "--dbname", database_name, "--command", clear_schemas_sql],
        env,
        timeout=300,
    )
    if cleared.returncode != 0:
        return cleared
    return _run_database_client(
        ["pg_restore", "--clean", "--if-exists", "--exit-on-error", "--single-transaction",
         "--no-owner", "--no-acl", "--dbname", database_name, dump_path],
        env,
    )


def _restore_previous_database(safety_path, database_name, env, original_error):
    rollback = _restore_database_dump(safety_path, database_name, env)
    if rollback.returncode != 0:
        raise RuntimeError(
            "Der Import ist fehlgeschlagen und auch die automatische Wiederherstellung der vorherigen "
            "Datenbank ist fehlgeschlagen. Bitte den Serverzustand sofort prüfen. "
            + rollback.stderr.decode("utf-8", "replace")[-1200:]
        ) from original_error
    raise RuntimeError(
        "Der Import bzw. die anschließende Datenbankmigration ist fehlgeschlagen. "
        "Die vorherige Datenbank wurde automatisch wiederhergestellt. "
        + str(original_error)
    ) from original_error


@login_required
@require_http_methods(["GET"])
def management_database_export(request):
    _require_admin(request)
    dump_path = archive_path = None
    try:
        env, database_name = _database_client_environment()
        migrations_before_dump = _database_schema_migrations()
        with tempfile.NamedTemporaryFile(prefix="meeting-manager-", suffix=".dump", delete=False) as handle:
            dump_path = handle.name
        result = _run_database_client(
            ["pg_dump", "--format=custom", "--no-owner", "--no-acl", "--file", dump_path, "--dbname", database_name],
            env,
        )
        if result.returncode != 0:
            raise RuntimeError(result.stderr.decode("utf-8", "replace")[-2000:] or "pg_dump ist fehlgeschlagen.")

        metadata = {
            "format_version": DATABASE_BACKUP_FORMAT_VERSION,
            "exported_at": timezone.now().isoformat(),
            "schema_migrations": migrations_before_dump,
        }
        with tempfile.NamedTemporaryFile(prefix="meeting-manager-backup-", suffix=".zip", delete=False) as handle:
            archive_path = handle.name
        with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_STORED) as archive:
            archive.write(dump_path, arcname="database.dump")
            archive.writestr(
                "metadata.json",
                json.dumps(metadata, ensure_ascii=False, indent=2).encode("utf-8"),
            )
        if _database_schema_migrations() != migrations_before_dump:
            raise RuntimeError(
                "Die Datenbankstruktur hat sich während des Exports geändert. "
                "Bitte den Export erneut starten."
            )

        stream = open(archive_path, "rb")
        response = FileResponse(
            stream, as_attachment=True, filename="meeting-manager-vollbackup.zip",
            content_type="application/zip",
        )
        response._resource_closers.append(
            lambda: (Path(dump_path).unlink(missing_ok=True), Path(archive_path).unlink(missing_ok=True))
        )
        return response
    except (OSError, RuntimeError, subprocess.TimeoutExpired, zipfile.BadZipFile) as exc:
        for path in (dump_path, archive_path):
            if path:
                Path(path).unlink(missing_ok=True)
        logger.exception("Vollständiger Datenbankexport fehlgeschlagen.")
        messages.error(request, f"Der Datenbankexport ist fehlgeschlagen: {exc}")
        return redirect("management_data")


@login_required
@require_http_methods(["POST"])
def management_database_import(request):
    _require_admin(request)
    uploaded = request.FILES.get("database_backup")
    if not uploaded:
        messages.error(request, "Bitte eine Datenbanksicherung auswählen.")
        return redirect("management_data")
    if uploaded.size > DATABASE_BACKUP_MAX_BYTES:
        messages.error(request, "Die Sicherungsdatei ist größer als das erlaubte Limit von 1 GiB.")
        return redirect("management_data")
    if request.POST.get("confirmation") != "DATENBANK ERSETZEN":
        messages.error(request, "Bitte bestätige den Import durch die Eingabe von DATENBANK ERSETZEN.")
        return redirect("management_data")

    uploaded_path = dump_path = safety_path = None
    try:
        env, database_name = _database_client_environment()
        with tempfile.NamedTemporaryFile(prefix="meeting-manager-upload-", suffix=".zip", delete=False) as handle:
            uploaded_path = handle.name
            for chunk in uploaded.chunks():
                handle.write(chunk)

        with zipfile.ZipFile(uploaded_path, "r") as archive:
            entries = {item.filename: item for item in archive.infolist()}
            if set(entries) != {"metadata.json", "database.dump"} or len(archive.infolist()) != 2:
                raise RuntimeError("Die Sicherungsdatei besitzt nicht das erwartete Meeting-Manager-Backupformat.")
            metadata_info = entries["metadata.json"]
            dump_info = entries["database.dump"]
            if metadata_info.file_size > 1024 * 1024:
                raise RuntimeError("Die Metadaten der Sicherung sind ungewöhnlich groß.")
            if dump_info.file_size <= 0 or dump_info.file_size > DATABASE_BACKUP_MAX_BYTES:
                raise RuntimeError("Die Datenbanksicherung ist leer oder überschreitet das erlaubte Limit von 1 GiB.")
            metadata = json.loads(archive.read(metadata_info).decode("utf-8"))
            if not isinstance(metadata, dict) or metadata.get("format_version") != DATABASE_BACKUP_FORMAT_VERSION:
                raise RuntimeError("Die Backup-Formatversion wird von dieser Anwendung nicht unterstützt.")
            backup_migrations = _validate_backup_migrations(metadata.get("schema_migrations"))

            with tempfile.NamedTemporaryFile(prefix="meeting-manager-restore-", suffix=".dump", delete=False) as handle:
                dump_path = handle.name
                with archive.open(dump_info, "r") as source:
                    while chunk := source.read(1024 * 1024):
                        handle.write(chunk)

        listing = _run_database_client(["pg_restore", "--list", dump_path], env, timeout=120)
        if listing.returncode != 0:
            raise RuntimeError("Die Datenbankdatei im Backup ist kein gültiges PostgreSQL-Archiv.")

        with tempfile.NamedTemporaryFile(prefix="meeting-manager-before-restore-", suffix=".dump", delete=False) as handle:
            safety_path = handle.name
        backup = _run_database_client(
            ["pg_dump", "--format=custom", "--no-owner", "--no-acl", "--file", safety_path, "--dbname", database_name],
            env,
        )
        if backup.returncode != 0:
            raise RuntimeError(
                "Die aktuelle Datenbank konnte vor dem Import nicht gesichert werden. Import abgebrochen. "
                + backup.stderr.decode("utf-8", "replace")[-1200:]
            )

        restored = _restore_database_dump(dump_path, database_name, env)
        if restored.returncode != 0:
            _restore_previous_database(
                safety_path, database_name, env,
                restored.stderr.decode("utf-8", "replace")[-1200:] or "pg_restore ist fehlgeschlagen.",
            )

        try:
            connection.close()
            restored_migrations = set(MigrationRecorder(connection).applied_migrations())
            if restored_migrations != backup_migrations:
                raise RuntimeError(
                    "Die im Backup gespeicherte Migrationshistorie stimmt nicht mit der wiederhergestellten "
                    "Datenbank überein. Der Import wird zurückgerollt."
                )
            _validate_backup_migrations([
                {"app": app_label, "name": migration_name}
                for app_label, migration_name in sorted(restored_migrations)
            ])
            call_command("migrate", interactive=False, verbosity=0)
            executor = MigrationExecutor(connection)
            pending = executor.migration_plan(executor.loader.graph.leaf_nodes())
            if pending:
                raise RuntimeError("Nach der Migration sind weiterhin nicht angewendete Datenbankmigrationen vorhanden.")
        except Exception as migration_error:
            connection.close()
            _restore_previous_database(safety_path, database_name, env, migration_error)

        from django.contrib.auth import logout
        logout(request)
        messages.success(request, "Die Datenbank wurde importiert und auf den aktuellen Programmstand migriert. Bitte melde dich erneut an.")
        return redirect("login")
    except (OSError, RuntimeError, subprocess.TimeoutExpired, zipfile.BadZipFile, json.JSONDecodeError, UnicodeDecodeError) as exc:
        logger.exception("Vollständiger Datenbankimport fehlgeschlagen.")
        messages.error(request, f"Der Datenbankimport ist fehlgeschlagen: {exc}")
        return redirect("management_data")
    finally:
        for path in (uploaded_path, dump_path, safety_path):
            if path:
                Path(path).unlink(missing_ok=True)


@login_required
def management_data(request):
    _require_admin(request)
    return render(request, "meetings/management_data.html")


@login_required
def management_user_password_reset(request, pk):
    _require_admin(request)
    user = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        from django.contrib.auth.tokens import default_token_generator
        from django.utils.http import urlsafe_base64_encode
        from django.utils.encoding import force_bytes
        from django.urls import reverse
        from django.contrib.sites.shortcuts import get_current_site
        from django.core.mail import send_mail
        from django.template.loader import render_to_string
        from django.utils.html import strip_tags
        from django.contrib.auth.forms import PasswordResetForm
        form = PasswordResetForm({"email": user.email})
        if not user.email or not form.is_valid():
            messages.error(request, "Für diesen Nutzer ist keine gültige E-Mail-Adresse hinterlegt.")
        else:
            form.save(
                request=request,
                use_https=request.is_secure(),
                email_template_name="registration/password_reset_email.html",
                subject_template_name="registration/password_reset_subject.txt",
                domain_override=get_current_site(request).domain,
            )
            messages.success(request, "Die Passwort-Zurücksetzen-Mail wurde angefordert.")
        return redirect("management_user_edit", pk=user.pk)
    return render(request, "meetings/management_password_reset.html", {"account": user})


@login_required
def management_user_series(request, pk):
    _require_admin(request)
    user = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        selected = request.POST.getlist("series")
        roles = request.POST
        with transaction.atomic():
            for series in MeetingSeries.objects.all():
                role = roles.get(f"role_{series.pk}")
                if str(series.pk) in selected and role in dict(SeriesAccess.ROLE_CHOICES):
                    SeriesAccess.objects.update_or_create(user=user, series=series, defaults={"role": role})
                else:
                    SeriesAccess.objects.filter(user=user, series=series).delete()
        messages.success(request, "Besprechungsreihen-Zuordnungen wurden gespeichert.")
        return redirect("management_user_edit", pk=user.pk)
    return render(request, "meetings/management_user_series.html", {
        "account": user, "series_rows": [{
            "series": series,
            "access": SeriesAccess.objects.filter(user=user, series=series).first(),
        } for series in MeetingSeries.objects.order_by("name")],
        "role_choices": SeriesAccess.ROLE_CHOICES,
    })


@login_required
def management_user_csv_export(request):
    _require_admin(request)
    return export_users_csv(request)


@login_required
def management_user_csv_import(request):
    _require_admin(request)
    return import_users_csv(request)


@login_required
def management_topic_csv_export(request):
    _require_admin(request)
    return export_topic_agenda_csv(request)


@login_required
def management_topic_csv_sample(request):
    _require_admin(request)
    return sample_csv_response()


@login_required
def management_topic_csv_import(request):
    _require_admin(request)
    return import_topic_agenda_csv(request)


@login_required
def management_user_csv_sample(request):
    _require_admin(request)
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="benutzer-muster.csv"'
    response.write("\ufeff")
    response.write(
        "# Musterdatei fuer den Nutzerimport. UTF-8-Kodierung, Semikolon als Trennzeichen.\r\n"
        "# Kommentarzeilen mit # werden beim Import ignoriert und koennen in der Datei stehen bleiben.\r\n"
        "# username: Pflichtfeld; eindeutiger Anmeldename, maximal 150 Zeichen.\r\n"
        "# first_name: Vorname; optionaler Freitext.\r\n"
        "# last_name: Nachname; optionaler Freitext.\r\n"
        "# email: E-Mail-Adresse; optional, muss bei Angabe eindeutig sein.\r\n"
        "# short_description: Kurzbeschreibung; optional, maximal 80 Zeichen.\r\n"
        "# is_active: Konto aktivieren; erlaubt: true/false, 1/0, ja/nein, yes/no, aktiv/inaktiv, aktiviert/deaktiviert.\r\n"
        "# series: Name einer bereits vorhandenen Besprechungsreihe; optional, Schreibweise muss exakt uebereinstimmen.\r\n"
        "# series_role: Rolle fuer die angegebene Reihe; erlaubt: participant, teilnehmer*in, moderator, moderator*in, reader, leser*in.\r\n"
        "# series_role bleibt leer, wenn keine series angegeben ist. Bei mehreren Reihen je Benutzer eine Zeile verwenden; Nutzerdaten identisch halten.\r\n"
        "# is_administrator: Optionale globale Administratorrolle; erlaubt dieselben Ja/Nein-Werte wie is_active. Nur globale Administratoren duerfen dieses Feld importieren.\r\n"
        "# Neue Benutzer erhalten ein zufaelliges Startpasswort; anschliessend ist die Passwort-zuruecksetzen-Funktion zu verwenden.\r\n"
        "username;first_name;last_name;email;short_description;is_active;series;series_role;is_administrator\r\n"
        "musterbenutzer;Max;Mustermann;max.mustermann@example.org;Beispielkonto;true;;;false\r\n"
    )
    return response
