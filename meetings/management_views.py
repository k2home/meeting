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
from django.core.mail import send_mail
from django.conf import settings
from django.http import FileResponse, HttpResponse, JsonResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from .access import is_admin, is_auditor, is_moderator
from .models import AuditEvent, MeetingSeries, OrganizationSettings, SeriesAccess, Topic, UserProfile
from .user_csv import export_users_csv, import_users_csv
from .topic_csv import export_topic_agenda_csv, import_topic_agenda_csv, sample_csv_response
from .user_display import user_display_name_with_login
from .user_roles import USER_ROLE_CHOICES, get_user_role, sync_user_role
from .password_setup import start_password_setup

logger = logging.getLogger(__name__)

User = get_user_model()


def _testing_mode_enabled():
    return os.path.isfile("/var/lib/meeting-manager-updater/testing-mode")


def _require_admin(request):
    if not is_admin(request.user):
        raise PermissionDenied


def _record_system_change(*, actor, action, summary, changes=None):
    """Record administrative changes without attaching them to meeting-series data."""
    return AuditEvent.objects.create(
        actor=actor,
        scope=AuditEvent.SCOPE_SYSTEM,
        action=action,
        summary=summary[:500],
        changes=changes or {},
    )


class ManagedUserCreateForm(UserCreationForm):
    first_name = forms.CharField(label="Vorname", max_length=150, required=False)
    last_name = forms.CharField(label="Nachname", max_length=150, required=False)
    email = forms.EmailField(label="E-Mail-Adresse", required=False)
    short_description = forms.CharField(label="Kurzbeschreibung", max_length=80, required=False)
    role = forms.ChoiceField(label="Globale Berechtigung", choices=USER_ROLE_CHOICES, initial="user", required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "last_name", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.testing_mode = _testing_mode_enabled()
        self.fields["password1"].required = False
        self.fields["password2"].required = False
        self.fields["password1"].help_text = "Optional. Bleiben beide Felder leer, gilt das in der Organisationsverwaltung konfigurierte Startpasswort. Der Nutzer muss innerhalb von 24 Stunden ein persönliches Passwort festlegen."
        self.fields["password2"].help_text = "Nur ausfüllen, wenn direkt ein persönliches Passwort vergeben werden soll."

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if not password1 and not password2:
            return None
        if password1 != password2:
            raise ValidationError(self.error_messages["password_mismatch"], code="password_mismatch")
        return password2

    def _post_clean(self):
        if self.testing_mode:
            # BaseUserCreationForm._post_clean runs password validators even
            # when clean_password2 skips them. Call ModelForm directly here
            # so model validation remains active without password-policy checks.
            forms.ModelForm._post_clean(self)
        else:
            super()._post_clean()

    def save(self, commit=True):
        user = super().save(commit=False)
        passwordless_creation = not self.cleaned_data.get("password1")
        if passwordless_creation:
            user.set_password(OrganizationSettings.current_start_password())
        for field in ("first_name", "last_name", "email"):
            setattr(user, field, self.cleaned_data.get(field, "").strip())
        if commit:
            user.save()
            UserProfile.objects.update_or_create(
                user=user,
                defaults={
                    "short_description": self.cleaned_data.get("short_description", "").strip(),
                    "must_change_password": passwordless_creation,
                    "password_setup_expires_at": timezone.now() + timedelta(hours=24) if passwordless_creation else None,
                },
            )
            sync_user_role(user, self.cleaned_data.get("role") or "user")
        return user


class ManagedUserEditForm(forms.ModelForm):
    is_active = forms.ChoiceField(label="Aktiv", choices=(("true", "Aktiv"), ("false", "Deaktiviert")))
    short_description = forms.CharField(label="Organisationskennzeichen", max_length=80, required=False)
    role = forms.ChoiceField(label="Globale Berechtigung", choices=USER_ROLE_CHOICES)

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "is_active")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].disabled = True
        self.initial["is_active"] = "true" if self.instance.is_active else "false"
        profile = getattr(self.instance, "meeting_profile", None) if self.instance.pk else None
        self.fields["short_description"].initial = profile.short_description if profile else ""
        self.fields["last_login"] = forms.CharField(label="Letzte Anmeldung", required=False, disabled=True, initial=self.instance.last_login.strftime("%d.%m.%Y, %H:%M") if self.instance.last_login else "Noch nie")
        self.fields["date_joined"] = forms.CharField(label="Erstellt am", required=False, disabled=True, initial=self.instance.date_joined.strftime("%d.%m.%Y, %H:%M") if self.instance.date_joined else "–")
        self.fields["role"].initial = get_user_role(self.instance) if self.instance.pk else "user"
        if self.instance.is_superuser:
            self.fields["role"].disabled = True

    def clean_is_active(self):
        return self.cleaned_data["is_active"] == "true"

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            UserProfile.objects.update_or_create(
                user=user, defaults={"short_description": self.cleaned_data.get("short_description", "").strip()}
            )
            sync_user_role(user, self.cleaned_data["role"])
        return user


class OrganizationSettingsForm(forms.ModelForm):
    retention_years = forms.IntegerField(
        label="Zentrale Aufbewahrungsfrist (Jahre)",
        min_value=1,
        widget=forms.NumberInput(attrs={"min": "1", "step": "1", "inputmode": "numeric"}),
    )
    timezone = forms.ChoiceField(
        label="Zeitzone",
        choices=[(zone, zone) for zone in sorted(available_timezones())],
    )
    start_password = forms.CharField(
        label="Startpasswort",
        strip=False,
        widget=forms.TextInput(attrs={"autocomplete": "off"}),
        help_text="Ohne Komplexitätsvorgaben. Wird bei passwortloser Benutzeranlage, Passwort-Reset und Freischaltung verwendet.",
    )

    class Meta:
        model = OrganizationSettings
        fields = (
            "name", "short_name", "timezone", "start_password", "retention_years", "attachment_max_size_mb",
            "primary_color", "primary_color_light", "primary_color_dark",
            "secondary_color", "secondary_color_light", "secondary_color_dark",
            "tertiary_color", "tertiary_color_light", "tertiary_color_dark",
        )


class OrganizationLogoForm(forms.ModelForm):
    class Meta:
        model = OrganizationSettings
        fields = ("logo",)
        labels = {"logo": "Neues Logo auswählen"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["logo"].widget = forms.FileInput(attrs={
            "accept": ".png,.jpg,.jpeg,.svg,image/png,image/jpeg,image/svg+xml",
        })


@login_required
def management_home(request):
    _require_admin(request)
    return render(request, "meetings/management.html", {
        "user_count": User.objects.count(),
        "active_user_count": User.objects.filter(is_active=True).count(),
        "series_count": MeetingSeries.objects.count(),
    })


@login_required
def auditor_overview(request):
    if not is_auditor(request.user):
        return redirect("dashboard")
    return render(request, "meetings/auditor_overview.html", {
        "organization_settings": OrganizationSettings.objects.filter(pk=1).defer("start_password").first(),
    })


@login_required
def auditor_organization_settings(request):
    if not is_auditor(request.user):
        return redirect("management_settings")
    if request.method != "GET":
        return HttpResponseForbidden("Auditor*innen haben ausschließlich Lesezugriff.")
    instance = OrganizationSettings.objects.filter(pk=1).defer("start_password").first()
    return render(request, "meetings/auditor_organization_settings.html", {"settings": instance})


@login_required
def auditor_users(request):
    if request.method != "GET":
        return HttpResponseForbidden("Auditor*innen haben ausschließlich Lesezugriff.")
    if not is_auditor(request.user):
        return redirect("management_users")
    users = User.objects.select_related("meeting_profile").all().order_by("last_name", "first_name", "username")
    return render(request, "meetings/auditor_users.html", {
        "users": [{
            "account": user,
            "organization_label": getattr(getattr(user, "meeting_profile", None), "short_description", ""),
            "role_label": dict(USER_ROLE_CHOICES)[get_user_role(user)],
        } for user in users],
    })


@login_required
def auditor_groups(request):
    if request.method != "GET":
        return HttpResponseForbidden("Auditor*innen haben ausschließlich Lesezugriff.")
    if not is_auditor(request.user):
        return redirect("management_groups")
    access_qs = SeriesAccess.objects.select_related("series", "user").all()
    query = request.GET.get("q", "").strip()
    role_filter = request.GET.get("role", "")
    if query:
        from django.db.models import Q
        access_qs = access_qs.filter(
            Q(user__username__icontains=query) |
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(series__name__icontains=query)
        )
    if role_filter in dict(SeriesAccess.ROLE_CHOICES):
        access_qs = access_qs.filter(role=role_filter)
    access_ids = set(access_qs.values_list("pk", flat=True))
    series_rows = [{
        "series": series,
        "members": [access for access in series.user_access.select_related("user").all() if access.pk in access_ids],
    } for series in MeetingSeries.objects.order_by("name")]
    series_rows = [row for row in series_rows if row["members"] or not (query or role_filter)]
    return render(request, "meetings/auditor_groups.html", {
        "series_rows": series_rows,
        "search": query,
        "role_filter": role_filter,
        "role_choices": SeriesAccess.ROLE_CHOICES,
    })


@login_required
def management_users(request):
    _require_admin(request)
    users = User.objects.select_related("meeting_profile").all().order_by("last_name", "first_name", "username")
    return render(request, "meetings/management_users.html", {
        "users": [{
            "account": user,
            "organization_label": getattr(getattr(user, "meeting_profile", None), "short_description", ""),
            "role": get_user_role(user),
            "role_label": dict(USER_ROLE_CHOICES)[get_user_role(user)],
        } for user in users],
        "role_choices": SeriesAccess.ROLE_CHOICES,
    })


@login_required
def management_user_edit(request, pk=None):
    _require_admin(request)
    instance = get_object_or_404(User, pk=pk) if pk else None
    # ModelForm validation updates its instance in memory. Capture the old
    # state before is_valid(), otherwise reactivation and audit diffs are lost.
    was_inactive = bool(instance and not instance.is_active)
    before = {
        "Vorname": instance.first_name,
        "Nachname": instance.last_name,
        "E-Mail": instance.email,
        "Aktiv": instance.is_active,
        "Globale Rolle": dict(USER_ROLE_CHOICES).get(get_user_role(instance), get_user_role(instance)),
        "Organisationskennzeichen": getattr(getattr(instance, "meeting_profile", None), "short_description", ""),
    } if instance else {}
    if instance:
        form = ManagedUserEditForm(request.POST or None, instance=instance)
    else:
        form = ManagedUserCreateForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        if instance and instance.pk == request.user.pk and not form.cleaned_data["is_active"]:
            form.add_error("is_active", "Das eigene Administratorkonto kann hier nicht deaktiviert werden.")
        else:
            with transaction.atomic():
                passwordless_creation = not instance and not form.cleaned_data.get("password1")
                user = form.save()
                if was_inactive and user.is_active:
                    start_password_setup(user)
                after = {
                    "Vorname": user.first_name,
                    "Nachname": user.last_name,
                    "E-Mail": user.email,
                    "Aktiv": user.is_active,
                    "Globale Rolle": dict(USER_ROLE_CHOICES).get(get_user_role(user), get_user_role(user)),
                    "Organisationskennzeichen": getattr(getattr(user, "meeting_profile", None), "short_description", ""),
                }
                changes = {
                    label: {"vorher": before.get(label), "nachher": value}
                    for label, value in after.items()
                    if before.get(label) != value
                } if instance else {
                    label: {"nachher": value} for label, value in after.items()
                }
                _record_system_change(
                    actor=request.user,
                    action="updated" if instance else "created",
                    summary=f"Benutzerkonto „{user_display_name_with_login(user)}“ {'geändert' if instance else 'angelegt'}",
                    changes=changes,
                )
            if was_inactive and user.is_active:
                messages.success(request, f"Benutzer „{user_display_name_with_login(user)}“ wurde freigeschaltet. Das konfigurierte Startpasswort gilt für die nächsten 24 Stunden.")
            else:
                messages.success(request, f"Benutzer „{user_display_name_with_login(user)}“ wurde gespeichert.")
            return redirect("management_users")
    return render(request, "meetings/management_user_form.html", {
        "form": form, "page_title": "Benutzer bearbeiten" if instance else "Benutzer hinzufügen",
        "is_new": instance is None, "testing_mode": _testing_mode_enabled(),
    })


@login_required
@require_http_methods(["POST"])
def management_user_delete(request, pk):
    _require_admin(request)
    user = get_object_or_404(User, pk=pk)
    if user.pk == request.user.pk:
        messages.error(request, "Das eigene Administratorkonto kann nicht gelöscht werden.")
        return redirect("management_users")
    display_name = user_display_name_with_login(user)
    changes = {
        "Benutzername": {"vorher": user.username, "nachher": None},
        "Name": {"vorher": " ".join(part for part in (user.first_name, user.last_name) if part), "nachher": None},
        "E-Mail": {"vorher": user.email, "nachher": None},
        "Globale Rolle": {"vorher": dict(USER_ROLE_CHOICES).get(get_user_role(user), get_user_role(user)), "nachher": None},
    }
    with transaction.atomic():
        _record_system_change(actor=request.user, action="deleted", summary=f"Benutzerkonto „{display_name}“ gelöscht", changes=changes)
        user.delete()
    messages.success(request, f"Benutzer „{display_name}“ wurde gelöscht.")
    return redirect("management_users")

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
    persisted_retention_years = instance.retention_years
    logo_form = OrganizationLogoForm(instance=instance)
    form = OrganizationSettingsForm(instance=instance)

    if request.method == "POST" and request.POST.get("action") == "reset_logo":
        previous_logo = instance.logo.name if instance.logo else ""
        previous_png = instance.logo_png.name if instance.logo_png else ""
        if previous_logo or previous_png:
            if instance.logo:
                instance.logo.delete(save=False)
            if instance.logo_png:
                instance.logo_png.delete(save=False)
            instance.save(update_fields=["logo", "logo_png"])
            _record_system_change(
                actor=request.user, action="updated",
                summary="Organisationslogo zurückgesetzt",
                changes={
                    "Organisationslogo": {
                        "vorher": previous_logo or "Kein Logo",
                        "nachher": "Kein Logo",
                    },
                },
            )
            messages.success(request, "Das Organisationslogo wurde zurückgesetzt.")
        else:
            messages.info(request, "Es ist kein Organisationslogo hinterlegt.")
        return redirect("management_settings")

    if request.method == "POST" and request.POST.get("action") == "save_logo":
        logo_form = OrganizationLogoForm(request.POST, request.FILES, instance=instance)
        if logo_form.is_valid():
            previous_logo = instance.logo.name if instance.logo else ""
            settings_obj = logo_form.save(commit=False)
            settings_obj.full_clean()
            settings_obj.save()
            uploaded_logo = settings_obj.logo
            if (uploaded_logo.name if uploaded_logo else "") != previous_logo:
                _record_system_change(
                    actor=request.user, action="updated",
                    summary="Organisationslogo geändert",
                    changes={"Organisationslogo": {"vorher": previous_logo or "Kein Logo", "nachher": uploaded_logo.name if uploaded_logo else "Kein Logo"}},
                )
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
            old_retention_years = persisted_retention_years
            new_retention_years = form.cleaned_data["retention_years"]
            retention_decision = request.POST.get("retention_change_decision", "")
            inherited_archived_count = Topic.objects.filter(
                status="archived", retention_years__isnull=True
            ).count()
            if (
                new_retention_years != old_retention_years
                and inherited_archived_count
                and retention_decision not in {"apply", "keep"}
            ):
                return render(request, "meetings/management_settings.html", {
                    "form": form, "logo_form": logo_form,
                    "organization_settings": instance,
                    "show_retention_confirmation": True,
                    "inherited_archived_count": inherited_archived_count,
                })
            before = {
                field: getattr(instance, field)
                for field in form.changed_data
                if field not in {"logo", "logo_png", "start_password"}
            }
            if "retention_years" in form.changed_data:
                before["retention_years"] = persisted_retention_years
            with transaction.atomic():
                if (
                    new_retention_years != old_retention_years
                    and inherited_archived_count
                    and retention_decision == "keep"
                ):
                    Topic.objects.filter(
                        status="archived", retention_years__isnull=True
                    ).update(retention_years=old_retention_years)
                settings_obj = form.save(commit=False)
                settings_obj.full_clean()
                settings_obj.save()
            changes = {
                form.fields[field].label: {"vorher": before[field], "nachher": getattr(settings_obj, field)}
                for field in before
                if before[field] != getattr(settings_obj, field)
            }
            if "start_password" in form.changed_data:
                changes["Startpasswort"] = {"nachher": "Geändert"}
            if changes:
                _record_system_change(
                    actor=request.user, action="updated",
                    summary="Organisationseinstellungen geändert", changes=changes,
                )
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

    try:
        current_migrations = MigrationLoader(None).graph.nodes
    except Exception as exc:
        raise RuntimeError("Die Datenbankmigrationen der aktuellen Programmversion sind nicht konsistent.") from exc
    unknown = sorted(normalized.difference(current_migrations))
    if unknown:
        details = ", ".join(f"{app}.{name}" for app, name in unknown[:10])
        raise RuntimeError(
            "Dieses Backup stammt aus einer neueren oder inkompatiblen Datenbankversion. "
            f"Die benötigten Migrationen sind im aktuellen Programm nicht vorhanden: {details}"
        )
    return normalized


def _clear_database_schemas(database_name, env):
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
    return _run_database_client(
        ["psql", "--set", "ON_ERROR_STOP=1", "--dbname", database_name, "--command", clear_schemas_sql],
        env,
        timeout=300,
    )


def _restore_database_dump(dump_path, database_name, env):
    cleared = _clear_database_schemas(database_name, env)
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
        _record_system_change(
            actor=request.user, action="created",
            summary="Vollständige Datenbanksicherung exportiert",
            changes={"Backup": {"nachher": "meeting-manager-vollbackup.zip"}, "Datenbankmigrationen": {"nachher": len(migrations_before_dump)}},
        )
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

    initiating_actor_id = request.user.pk
    initiating_actor_username = request.user.get_username()
    initiating_actor_label = user_display_name_with_login(request.user)
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

        cleared = _clear_database_schemas(database_name, env)
        if cleared.returncode != 0:
            raise RuntimeError(
                "Die vorhandenen Datenbankschemas konnten nicht sicher für den Import vorbereitet werden. "
                "Die Datenbank wurde nicht ersetzt. "
                + cleared.stderr.decode("utf-8", "replace")[-1200:]
            )
        restored = _run_database_client(
            ["pg_restore", "--clean", "--if-exists", "--exit-on-error", "--single-transaction",
             "--no-owner", "--no-acl", "--dbname", database_name, dump_path],
            env,
        )
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

        restored_actor = User.objects.filter(
            pk=initiating_actor_id, username=initiating_actor_username
        ).first()
        _record_system_change(
            actor=restored_actor,
            action="updated",
            summary=f"Vollständige Datenbanksicherung durch „{initiating_actor_label}“ importiert und Datenbank migriert",
            changes={
                "Backup-Datei": {"nachher": uploaded.name[:255]},
                "Backup-Größe": {"nachher": uploaded.size},
                "Datenbankmigrationen": {"nachher": len(backup_migrations)},
            },
        )
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
        start_password_setup(user)
        _record_system_change(
            actor=request.user, action="updated",
            summary=f"Passwortwechsel für „{user_display_name_with_login(user)}“ erzwungen",
            changes={"Passwortstatus": {"nachher": "Konfiguriertes Startpasswort gesetzt; persönliche Passwortvergabe innerhalb von 24 Stunden erforderlich"}},
        )
        messages.success(request, "Das konfigurierte Startpasswort wurde gesetzt. Der Benutzer muss sich innerhalb von 24 Stunden anmelden und ein persönliches Passwort festlegen.")
        return redirect("management_user_edit", pk=user.pk)
    return render(request, "meetings/management_password_reset.html", {
        "account": user,
        "start_password": OrganizationSettings.current_start_password(),
    })

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
    if not is_moderator(request.user):
        raise PermissionDenied
    series_ids = list(SeriesAccess.objects.filter(
        user=request.user, role=SeriesAccess.ROLE_MODERATOR
    ).values_list("series_id", flat=True))
    return export_topic_agenda_csv(request, allowed_series_ids=series_ids)


@login_required
def management_topic_csv_sample(request):
    _require_admin(request)
    return sample_csv_response()


@login_required
def management_topic_csv_import(request):
    if not is_moderator(request.user):
        raise PermissionDenied
    series_ids = list(SeriesAccess.objects.filter(
        user=request.user, role=SeriesAccess.ROLE_MODERATOR
    ).values_list("series_id", flat=True))
    return import_topic_agenda_csv(request, allowed_series_ids=series_ids)


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
        "# user_role: Globale Rolle; erlaubt: user, admin, auditor. Nur globale Administratoren duerfen dieses Feld importieren.\r\n"
        "# Neu angelegte Benutzerkonten erhalten das in der Organisationsverwaltung konfigurierte Startpasswort. Innerhalb von 24 Stunden muss ein eigenes Passwort festgelegt werden; andernfalls wird das Konto deaktiviert.\r\n"
        "username;first_name;last_name;email;short_description;is_active;user_role;series;series_role\r\n"
        "musterbenutzer;Max;Mustermann;max.mustermann@example.org;Beispielkonto;true;user;;;\r\n"
    )
    return response


# ---------------------------------------------------------------------------
# Zufällige Testdaten – ausschließlich im explizit aktivierten TESTING-Modus.
# ---------------------------------------------------------------------------
def _require_testing_mode():
    if not _testing_mode_enabled():
        from django.http import Http404
        raise Http404("Die Testdatenverwaltung ist nur im TESTING-Modus verfügbar.")


def _testing_count(request, key, default=5, maximum=100):
    try:
        value = int(request.POST.get(key, default))
    except (TypeError, ValueError):
        raise ValidationError("Bitte gib eine gültige Anzahl ein.")
    if not 1 <= value <= maximum:
        raise ValidationError(f"Die Anzahl muss zwischen 1 und {maximum} liegen.")
    return value


def _testing_agenda_texts(topic_title):
    """Build 100 distinct, topic-specific sample texts, each containing two sentences."""
    openings = [
        f"Zum Thema {topic_title} wird der aktuelle Sachstand zusammengefasst.",
        f"Die bisherige Entwicklung bei {topic_title} wird gemeinsam eingeordnet.",
        f"Für {topic_title} werden die wichtigsten Rahmenbedingungen vorgestellt.",
        f"Die Beteiligten betrachten den aktuellen Stand von {topic_title}.",
        f"Im Mittelpunkt steht die weitere Bearbeitung von {topic_title}.",
        f"Die bisherigen Erfahrungen zu {topic_title} werden ausgewertet.",
        f"Der nächste Umsetzungsschritt für {topic_title} wird vorbereitet.",
        f"Offene Aspekte rund um {topic_title} werden strukturiert betrachtet.",
        f"Die Ergebnisse der letzten Arbeitsschritte zu {topic_title} werden vorgestellt.",
        f"Die weitere Abstimmung zu {topic_title} wird besprochen.",
    ]
    conclusions = [
        "Anschließend werden offene Fragen gesammelt und nach Dringlichkeit geordnet.",
        "Dabei werden Abhängigkeiten geprüft und die nächsten Schritte festgehalten.",
        "Die Teilnehmenden gleichen unterschiedliche Einschätzungen ab und dokumentieren das Ergebnis.",
        "Mögliche Risiken werden bewertet und geeignete Gegenmaßnahmen vorgeschlagen.",
        "Zuständigkeiten werden geklärt und ein realistischer Zeitrahmen wird abgestimmt.",
        "Die verfügbaren Optionen werden verglichen und eine Empfehlung wird vorbereitet.",
        "Erforderliche Informationen werden zusammengetragen und für die nächste Beratung aufbereitet.",
        "Vereinbarte Maßnahmen werden priorisiert und zur weiteren Bearbeitung festgehalten.",
        "Der aktuelle Klärungsbedarf wird dokumentiert und ein Folgetermin wird vorbereitet.",
        "Zum Abschluss werden Entscheidungen und noch ausstehende Rückmeldungen protokolliert.",
    ]
    return [f"{opening} {conclusion}" for opening in openings for conclusion in conclusions]


def _testing_random_user(block_number, unique_number):
    import secrets
    from .models import UserProfile
    from .user_roles import sync_user_role

    first_names = [
        "Alex", "Sam", "Robin", "Mika", "Jana", "Lena", "Noah", "Mara",
        "Toni", "Kim", "Emma", "Paul", "Mia", "Leon", "Nina", "Jonas",
        "Lara", "Ben", "Clara", "Felix", "Sofia", "Oskar", "Ida", "Emil",
    ]
    last_names = [
        "Becker", "Fischer", "Wagner", "Schulz", "Hoffmann", "Koch", "Richter",
        "Wolf", "Schneider", "Weber", "Meyer", "Bauer", "Schröder", "Neumann",
        "Krüger", "Hartmann", "Lange", "Krause", "Zimmermann", "Braun", "Krüger",
        "Hofmann", "Schmitt", "Werner", "Schmitz", "Kraus", "Meier", "Lehmann",
        "Schmid", "Schulze", "Maier", "Köhler", "Herrmann", "König", "Walter",
        "Mayer", "Huber", "Kaiser", "Fuchs", "Peters", "Lang", "Scholz", "Möller",
        "Weiß", "Jung", "Hahn", "Schubert", "Vogel", "Friedrich", "Keller",
        "Günther", "Frank", "Berger", "Winkler", "Roth", "Beck", "Lorenz",
        "Baumann", "Franke", "Albrecht", "Winter", "Kramer", "Schumacher",
        "Ludwig", "Vogt", "Jäger", "Stein", "Otto", "Sommer", "Groß", "Seidel",
        "Heinrich", "Brandt", "Haas", "Schreiber", "Graf", "Schulte", "Dietrich",
        "Ziegler", "Kuhn", "Pohl", "Engel", "Horn", "Busch", "Bergmann",
        "Thomas", "Voigt", "Sauer", "Arnold", "Wolff", "Pfeiffer", "Lenz",
        "Böhm", "Unger", "Kühn", "Schenk", "Auer", "Ebert", "Heß", "Bender",
        "Ritter", "Conrad",
    ]

    first_name = secrets.choice(first_names)
    available_last_names = [
        name for name in last_names
        if not User.objects.filter(username=f"TEST{name}").exists()
    ]
    if not available_last_names:
        raise ValidationError("Alle verfügbaren TEST-Benutzernamen sind bereits vergeben.")
    last_name = secrets.choice(available_last_names)
    username = f"TEST{last_name}"
    email_name = f"{first_name}.{last_name}".replace(" ", "").lower()
    short_description = f"{block_number:02d}/{unique_number:02d}"

    user = User.objects.create_user(
        username=username,
        first_name=first_name,
        last_name=last_name,
        email=f"{email_name}@beliebig.de",
        password=OrganizationSettings.current_start_password(),
    )
    UserProfile.objects.create(
        user=user,
        short_description=short_description,
        must_change_password=True,
        password_setup_expires_at=timezone.now() + timedelta(hours=24),
    )
    sync_user_role(user, "user")
    return user

@login_required
@require_http_methods(["GET", "POST"])
def testing_fixtures(request):
    _require_admin(request)
    _require_testing_mode()

    from datetime import date
    import secrets
    from django.db import transaction
    from django.db.models import Q
    from .models import AgendaItem, Meeting, Topic
    from .services import generate_meetings

    series_names = [
        "TEST Digitalisierung",
        "TEST IT-Sicherheit",
        "TEST Datenschutz",
        "TEST Prozessoptimierung",
        "TEST Personalentwicklung",
        "TEST Projektmanagement",
        "TEST Infrastruktur",
        "TEST Cloud-Strategie",
        "TEST Kommunikation",
        "TEST Qualitätsmanagement",
        "TEST Risikomanagement",
        "TEST Nachhaltigkeit",
        "TEST Kundenservice",
        "TEST Datenmanagement",
        "TEST Automatisierung",
        "TEST Zusammenarbeit",
        "TEST Weiterbildung",
        "TEST Ressourcenplanung",
        "TEST Informationsmanagement",
        "TEST Compliance",
        "TEST Innovation",
        "TEST Change Management",
        "TEST Beschaffung",
        "TEST Gebäudemanagement",
        "TEST Notfallplanung",
        "TEST Softwareentwicklung",
        "TEST Netzwerk",
        "TEST Controlling",
        "TEST Dokumentation",
        "TEST Strategie",
    ]
    fixture_series_description = (
        "TEST-Fixture: Zufällig erzeugte Beispieldaten mit festem Wochentag und regelmäßigem Rhythmus."
    )

    def assign_fixture_access(series, fixture_users):
        SeriesAccess.objects.update_or_create(
            series=series, user=request.user,
            defaults={"role": SeriesAccess.ROLE_MODERATOR},
        )
        for index, fixture_user in enumerate(fixture_users):
            if index == 0 or secrets.randbelow(100) < 65:
                SeriesAccess.objects.get_or_create(
                    series=series, user=fixture_user,
                    defaults={"role": secrets.choice([
                        SeriesAccess.ROLE_PARTICIPANT,
                        SeriesAccess.ROLE_MODERATOR,
                        SeriesAccess.ROLE_READER,
                    ])},
                )

    # A page token makes browser retries/double clicks harmless. It is
    # consumed on the first POST and must be refreshed after the redirect.
    nonce = request.POST.get("fixture_nonce") if request.method == "POST" else None
    if request.method == "GET":
        import secrets as _secrets
        fixture_nonce = _secrets.token_urlsafe(24)
        request.session["testing_fixture_nonce"] = fixture_nonce
    else:
        fixture_nonce = request.session.pop("testing_fixture_nonce", None)


    # Only operate on records created by this fixture tool; never bulk-edit real data.
    series_qs = MeetingSeries.objects.filter(
        Q(name__startswith="TEST-Besprechungsreihe ") | Q(description__startswith="TEST-Fixture:")
    ).order_by("name")
    topics_qs = Topic.objects.filter(Q(title__startswith="TEST-") | Q(title__startswith="TEST ")).select_related("series").order_by("title")
    if request.method == "POST":
        action = request.POST.get("action", "")
        try:
            with transaction.atomic():
                if not nonce or nonce != fixture_nonce:
                    raise ValidationError("Diese Aktion wurde bereits verarbeitet oder das Formular ist abgelaufen. Bitte lade die Seite neu.")
                if action == "create_series":
                    count = _testing_count(request, "series_count")
                    created = []
                    # Use a shared, explicit test window and a single weekday
                    # per series. Meetings are generated from the recurrence,
                    # never from independently randomized dates.
                    start_window = date(2026, 1, 1)
                    end_window = date(2027, 3, 31)
                    fixture_users = list(User.objects.filter(is_active=True, username__startswith="TEST", email__endswith="@beliebig.de"))
                    for _ in range(count):
                        recurrence = secrets.choice(["weekly", "biweekly", "monthly"])
                        interval = secrets.choice([1, 2, 3])
                        weekday = secrets.randbelow(5)
                        start_date = start_window
                        end_date = end_window
                        series = MeetingSeries.objects.create(
                            name=secrets.choice(series_names),
                            description=fixture_series_description,
                            active=True,
                            recurrence=recurrence,
                            recurrence_interval=interval,
                            weekday=weekday,
                            start_date=start_date,
                            end_date=end_date,
                        )
                        assign_fixture_access(series, fixture_users)
                        created.append(series)
                    messages.success(request, f"{len(created)} zufällige Besprechungsserien mit jeweils festem Wochentag und Rhythmus wurden angelegt.")
                elif action == "generate_meetings":
                    ids = request.POST.getlist("series_ids")
                    selected = series_qs.filter(pk__in=ids)
                    if not ids:
                        raise ValidationError("Bitte wähle mindestens eine Besprechungsserie aus.")
                    if not selected.exists():
                        raise ValidationError("Die Auswahl enthält keine gültige Besprechungsserie.")
                    created_count = 0
                    fixture_users = list(User.objects.filter(is_active=True, username__startswith="TEST", email__endswith="@beliebig.de"))
                    for series in selected.select_for_update():
                        assign_fixture_access(series, fixture_users)
                        created_count += len(generate_meetings(series, include_past=True))
                    messages.success(request, f"{created_count} neue Termine wurden für {selected.count()} Serien generiert.")
                elif action == "create_topics":
                    count = _testing_count(request, "topic_count")
                    series = get_object_or_404(series_qs, pk=request.POST.get("series_id"))
                    assign_fixture_access(
                        series, list(User.objects.filter(is_active=True, username__startswith="TEST", email__endswith="@beliebig.de"))
                    )
                    active_users = list(User.objects.filter(is_active=True, username__startswith="TEST", email__endswith="@beliebig.de"))
                    topic_names = [
                        "Umsetzung Projekt",
                        "Digitale Strategie",
                        "IT Sicherheit",
                        "Datenschutz Konzept",
                        "Prozess Analyse",
                        "Qualitätsmanagement",
                        "Personalentwicklung",
                        "Projekt Steuerung",
                        "Cloud Migration",
                        "Daten Analyse",
                        "Software Einführung",
                        "Netzwerk Planung",
                        "System Wartung",
                        "Ressourcen Planung",
                        "Risiko Bewertung",
                        "Notfall Management",
                        "Change Management",
                        "Kunden Service",
                        "Wissens Transfer",
                        "Team Zusammenarbeit",
                        "Dokumenten Verwaltung",
                        "Schnittstellen Prüfung",
                        "Automatisierung Prozesse",
                        "Betriebs Optimierung",
                        "Infrastruktur Ausbau",
                        "Schulungs Konzept",
                        "Budget Planung",
                        "Aufgaben Verteilung",
                        "Termin Koordination",
                        "Anforderungs Management",
                        "Technische Architektur",
                        "Berechtigungs Konzept",
                        "Sicherheits Prüfung",
                        "Daten Migration",
                        "Release Planung",
                        "Fehler Analyse",
                        "Support Prozesse",
                        "Kommunikations Konzept",
                        "Lieferanten Bewertung",
                        "Vertrags Management",
                        "Nachhaltige Beschaffung",
                        "Service Qualität",
                        "Arbeitsplatz Gestaltung",
                        "Mobile Anwendungen",
                        "Backup Strategie",
                        "Monitoring Konzept",
                        "Performance Analyse",
                        "Digitale Akten",
                        "Workflow Optimierung",
                        "Zukunfts Planung",
                    ]
                    existing_titles = set(
                        Topic.objects.filter(series=series, title__startswith="TEST ")
                        .values_list("title", flat=True)
                    )
                    available_names = [
                        name for name in topic_names if f"TEST {name}" not in existing_titles
                    ]
                    if count > len(available_names):
                        raise ValidationError(
                            f"Für diese Serie gibt es nur {len(available_names)} noch nicht verwendete Beispielthemen. "
                            "Bitte reduziere die Anzahl oder verwende eine weitere Testserie."
                        )
                    selected_names = secrets.SystemRandom().sample(available_names, count)
                    for name in selected_names:
                        Topic.objects.create(
                            title=f"TEST {name}",
                            series=series,
                            assigned_to=secrets.choice(active_users) if active_users and secrets.randbelow(2) else None,
                            status=secrets.choice(["open", "in_progress", "done"]),
                        )
                    messages.success(request, f"{count} zufällige Themen wurden für „{series.name}“ angelegt.")
                elif action == "create_agenda_items":
                    count = _testing_count(request, "agenda_count")
                    topic = get_object_or_404(topics_qs, pk=request.POST.get("topic_id"))
                    if not topic.series_id:
                        raise ValidationError("Das ausgewählte Thema ist keiner Besprechungsserie zugeordnet.")
                    assign_fixture_access(
                        topic.series, list(User.objects.filter(is_active=True, username__startswith="TEST", email__endswith="@beliebig.de"))
                    )
                    meetings = list(Meeting.objects.filter(series=topic.series, finalized_at__isnull=True).order_by("date"))
                    if not meetings:
                        raise ValidationError("Für diese Serie gibt es noch keine offenen Termine. Bitte zuerst Termine generieren.")
                    active_users = list(User.objects.filter(is_active=True, username__startswith="TEST", email__endswith="@beliebig.de"))
                    existing_items = list(
                        AgendaItem.objects.filter(topic=topic, meeting__series=topic.series)
                        .select_related("meeting").order_by("meeting__date", "pk")
                    )
                    last_item = existing_items[-1] if existing_items else None
                    candidates = [
                        meeting for meeting in meetings
                        if (last_item is None or meeting.date > last_item.meeting.date)
                        and not meeting.agenda_items.filter(topic=topic).exists()
                    ]
                    if not candidates:
                        raise ValidationError("Das Thema steht bereits auf allen verfügbaren Terminen dieser Serie.")
                    if len(candidates) < count:
                        raise ValidationError(
                            f"Es gibt nur {len(candidates)} freie Termine. Bitte generiere weitere Termine oder reduziere die Anzahl."
                        )
                    text_templates = _testing_agenda_texts(topic.title)
                    created_items = []
                    for index in range(count):
                        meeting = candidates[index]
                        previous_item = created_items[-1] if created_items else last_item
                        item = AgendaItem.objects.create(
                            meeting=meeting, topic=topic,
                            position=meeting.agenda_items.count(),
                            status=secrets.choice(["open", "in_progress", "done"]),
                            assigned_to=secrets.choice(active_users) if active_users and secrets.randbelow(2) else None,
                            working_text=secrets.choice(text_templates).format(topic=topic.title),
                            followup_of=previous_item,
                        )
                        created_items.append(item)
                    messages.success(
                        request,
                        f"{len(created_items)} Tagesordnungspunkte mit themenbezogenen Texten und chronologischer Wiedervorlage wurden angelegt."
                    )
                elif action == "create_users":
                    count = _testing_count(request, "user_count", maximum=100)
                    from .models import UserProfile
                    import re

                    used_blocks = set()
                    for description in UserProfile.objects.filter(
                        user__username__startswith="TEST", user__email__endswith="@beliebig.de"
                    ).values_list("short_description", flat=True):
                        match = re.match(r"^(\\d{2})/\\d{2}$", description or "")
                        if match:
                            used_blocks.add(int(match.group(1)))

                    available_blocks = [
                        block for block in range(100)
                        if block not in used_blocks
                    ]
                    if not available_blocks:
                        raise ValidationError("Alle 100 Kurzbezeichnungsblöcke sind bereits vergeben.")

                    block_number = secrets.choice(available_blocks)
                    unique_numbers = list(range(100))
                    secrets.SystemRandom().shuffle(unique_numbers)
                    if count > len(unique_numbers):
                        raise ValidationError("Ein Kurzbezeichnungsblock kann höchstens 100 Testnutzer enthalten.")

                    for unique_number in unique_numbers[:count]:
                        _testing_random_user(block_number, unique_number)
                    messages.success(
                        request,
                        f"{count} zufällige Testnutzer wurden im Kurzbezeichnungsblock "
                        f"{block_number:02d} angelegt. Für alle gilt das konfigurierte Startpasswort; es muss innerhalb von 24 Stunden geändert werden."
                    )
                elif action == "reset_fixtures":
                    test_series = list(series_qs)
                    test_series_ids = [series.pk for series in test_series]
                    test_topics = list(topics_qs)
                    meeting_count = Meeting.objects.filter(series_id__in=test_series_ids).count()
                    topic_count = len(test_topics)
                    series_count = len(test_series)
                    Meeting.objects.filter(series_id__in=test_series_ids).delete()
                    protected_topics = 0
                    for topic in test_topics:
                        try:
                            topic.delete()
                        except Exception as exc:
                            from django.db.models.deletion import ProtectedError
                            if not isinstance(exc, ProtectedError):
                                raise
                            protected_topics += 1
                    MeetingSeries.objects.filter(pk__in=test_series_ids).delete()
                    deleted_users = 0
                    protected_users = 0
                    for fixture_user in User.objects.filter(username__startswith="TEST", email__endswith="@beliebig.de").exclude(pk=request.user.pk):
                        in_use = (
                            fixture_user.meeting_participations.exists()
                            or fixture_user.assigned_meeting_topics.exists()
                            or fixture_user.assigned_meeting_agenda_items.exists()
                            or fixture_user.meeting_topic_comments.exists()
                            or fixture_user.meeting_series_access.exclude(
                                series__in=series_qs
                            ).exists()
                        )
                        if in_use:
                            protected_users += 1
                            continue
                        fixture_user.delete()
                        deleted_users += 1
                    messages.success(
                        request,
                        f"TEST-Daten zurückgesetzt: {series_count} Serien, {meeting_count} Termine, "
                        f"{topic_count - protected_topics} Themen und {deleted_users} Testnutzer gelöscht. "
                        f"{protected_topics} anderweitig verwendete Themen und {protected_users} Testnutzer blieben erhalten."
                    )
                else:
                    raise ValidationError("Unbekannte Testdatenaktion.")
        except ValidationError as exc:
            messages.error(request, " ".join(exc.messages))
        except Exception as exc:
            logger.exception("Fehler beim Erzeugen von Testdaten")
            messages.error(request, f"Testdaten konnten nicht vollständig erzeugt werden: {exc}")
        return redirect("testing_fixtures")

    return render(request, "meetings/testing_fixtures.html", {
        "fixture_nonce": fixture_nonce,
        "series_options": series_qs,
        "topic_options": topics_qs,
        "series_count": series_qs.count(),
        "meeting_count": Meeting.objects.filter(series__in=series_qs).count(),
        "fixture_user_count": User.objects.filter(username__startswith="TEST", email__endswith="@beliebig.de").count(),
        "testing_mode": True,
    })
