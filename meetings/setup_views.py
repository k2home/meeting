import logging
from io import StringIO
from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.core.management import call_command
from django.db import connection, transaction
from django.db.migrations.executor import MigrationExecutor
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from .forms_setup import InitialAdministratorForm
from .management_views import OrganizationLogoForm, OrganizationSettingsForm
from .models import OrganizationSettings
from .user_roles import sync_admin_access

logger = logging.getLogger(__name__)
User = get_user_model()
SETUP_LOCK_ID = 741029381
SETUP_STEPS = (("account", "Administrator"), ("organization", "Organisation"), ("system", "Systemprüfung"), ("complete", "Abschluss"))


def _setup_checks():
    checks = []
    try:
        connection.ensure_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        checks.append({"label": "Datenbankverbindung", "ok": True, "detail": "Die Datenbank ist erreichbar."})
    except Exception as exc:
        logger.exception("Setup-Prüfung: Datenbankverbindung fehlgeschlagen")
        checks.append({"label": "Datenbankverbindung", "ok": False, "detail": str(exc)})

    try:
        executor = MigrationExecutor(connection)
        pending = executor.migration_plan(executor.loader.graph.leaf_nodes())
        ok = not pending
        checks.append({
            "label": "Datenbankmigrationen", "ok": ok,
            "detail": "Alle Migrationen sind angewendet." if ok else f"{len(pending)} Migration(en) stehen noch aus.",
        })
    except Exception as exc:
        logger.exception("Setup-Prüfung: Migrationen konnten nicht geprüft werden")
        checks.append({"label": "Datenbankmigrationen", "ok": False, "detail": str(exc)})

    for label, directory in (("Medienverzeichnis", settings.MEDIA_ROOT), ("Verzeichnis für statische Dateien", settings.STATIC_ROOT)):
        path = Path(directory)
        ok = path.is_dir() and path.exists()
        if ok:
            import os
            ok = os.access(path, os.W_OK)
        checks.append({
            "label": label, "ok": ok,
            "detail": f"{path} ist vorhanden und beschreibbar." if ok else f"{path} fehlt oder ist nicht beschreibbar.",
        })

    key_ok = bool(settings.SECRET_KEY and "unsafe-development-key" not in settings.SECRET_KEY)
    checks.append({
        "label": "Sicherheitsschlüssel", "ok": key_ok,
        "detail": "Ein Anwendungsschlüssel ist konfiguriert." if key_ok else "SECRET_KEY fehlt oder verwendet den unsicheren Entwicklungswert.",
    })

    try:
        output = StringIO()
        call_command("check", stdout=output, stderr=output)
        checks.append({"label": "Django-Systemprüfung", "ok": True, "detail": "Keine Systemfehler gemeldet."})
    except Exception as exc:
        checks.append({"label": "Django-Systemprüfung", "ok": False, "detail": str(exc)})

    return checks


def _save_organization(request):
    instance = OrganizationSettings.objects.filter(pk=1).first() or OrganizationSettings()
    form = OrganizationSettingsForm(request.POST, instance=instance)
    logo_form = OrganizationLogoForm(request.POST, request.FILES, instance=instance)
    if not form.is_valid() or not logo_form.is_valid():
        return form, logo_form, False

    with transaction.atomic():
        settings_obj = form.save(commit=False)
        settings_obj.full_clean()
        settings_obj.save()
        if request.FILES.get("logo"):
            logo_form.instance = settings_obj
            logo_form.save()
            uploaded_logo = settings_obj.logo
            if uploaded_logo and uploaded_logo.name.lower().endswith(".svg"):
                try:
                    import cairosvg
                    from django.core.files.base import ContentFile
                    uploaded_logo.open("rb")
                    try:
                        svg_data = uploaded_logo.read()
                    finally:
                        uploaded_logo.close()
                    png_data = cairosvg.svg2png(bytestring=svg_data, output_width=1600, background_color="#ffffff")
                    png_name = uploaded_logo.name.rsplit("/", 1)[-1].rsplit(".", 1)[0] + ".png"
                    settings_obj.logo_png.save(png_name, ContentFile(png_data), save=True)
                except Exception:
                    logger.exception("Organisationslogo konnte nicht für den PDF-Export konvertiert werden.")
                    logo_form.add_error("logo", "Das Logo konnte nicht verarbeitet werden. Bitte PNG oder JPEG verwenden.")
                    return form, logo_form, False
    return form, logo_form, True


@require_http_methods(["GET", "POST"])
def setup_wizard(request):
    step = request.GET.get("step", "account")
    if step not in {"account", "organization", "system", "complete"}:
        step = "account"

    if not User.objects.exists():
        if step != "account":
            step = "account"
        if request.method == "POST":
            form = InitialAdministratorForm(request.POST)
            if form.is_valid():
                try:
                    with transaction.atomic():
                        if connection.vendor == "postgresql":
                            with connection.cursor() as cursor:
                                cursor.execute("SELECT pg_advisory_xact_lock(%s)", [SETUP_LOCK_ID])
                        if User.objects.exists():
                            return redirect("login")
                        user = form.save(commit=False)
                        user.is_superuser = True
                        user.is_staff = True
                        user.is_active = True
                        user.save()
                        sync_admin_access(user, True)
                    login(request, user, backend="django.contrib.auth.backends.ModelBackend")
                    request.session["initial_setup_user_id"] = user.pk
                    return redirect("/setup/?step=organization")
                except Exception:
                    logger.exception("Erstanlage des Administratorkontos fehlgeschlagen")
                    form.add_error(None, "Das Administratorkonto konnte nicht angelegt werden. Bitte erneut versuchen.")
        else:
            form = InitialAdministratorForm()
        return render(request, "meetings/setup_wizard.html", {"step": "account", "form": form, "setup_steps": SETUP_STEPS})

    setup_user_id = request.session.get("initial_setup_user_id")
    if not request.user.is_authenticated or not request.user.is_superuser or setup_user_id != request.user.pk:
        return redirect("login" if not request.user.is_authenticated else "dashboard")

    instance = OrganizationSettings.objects.filter(pk=1).first() or OrganizationSettings()
    form = OrganizationSettingsForm(instance=instance)
    logo_form = OrganizationLogoForm(instance=instance)

    if step == "organization":
        if request.method == "POST":
            form, logo_form, saved = _save_organization(request)
            if saved:
                request.session["initial_setup_organization_saved"] = True
                return redirect("/setup/?step=system")
        return render(request, "meetings/setup_wizard.html", {
            "step": step, "form": form, "logo_form": logo_form, "organization_settings": instance, "setup_steps": SETUP_STEPS,
        })

    if step == "system":
        checks = _setup_checks()
        all_ok = all(item["ok"] for item in checks)
        if request.method == "POST" and all_ok:
            return redirect("/setup/?step=complete")
        return render(request, "meetings/setup_wizard.html", {
            "step": step, "checks": checks, "all_checks_ok": all_ok, "setup_steps": SETUP_STEPS,
        })

    if step == "complete":
        if not request.session.get("initial_setup_organization_saved"):
            return redirect("/setup/?step=organization")
        checks = _setup_checks()
        all_ok = all(item["ok"] for item in checks)
        if request.method == "POST" and all_ok:
            request.session.pop("initial_setup_user_id", None)
            request.session.pop("initial_setup_organization_saved", None)
            messages.success(request, "Die Ersteinrichtung ist abgeschlossen. Willkommen im Meeting Manager!")
            return redirect("dashboard")
        return render(request, "meetings/setup_wizard.html", {
            "step": step, "checks": checks, "all_checks_ok": all_ok,
        })

    return redirect("/setup/?step=organization")
