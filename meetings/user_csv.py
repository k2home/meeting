import csv
import io
import secrets
from collections import OrderedDict

from django import forms
from django.contrib import admin, messages
from django.contrib.auth import get_user_model
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils.crypto import get_random_string

from .models import MeetingSeries, SeriesAccess, UserProfile
from .user_roles import sync_admin_access

User = get_user_model()

EXPORT_FIELDS = (
    "username", "first_name", "last_name", "email", "short_description",
    "is_active", "is_administrator", "series",
)
IMPORT_FIELDS = (
    "username", "first_name", "last_name", "email", "short_description",
    "is_active", "series", "series_role",
)
LEGACY_EXPORT_ONLY_FIELDS = ("date_joined", "last_login")  # accepted from older exports; never overwritten on import
ACCEPTED_FIELDS = IMPORT_FIELDS + ("is_administrator",) + LEGACY_EXPORT_ONLY_FIELDS
MAX_IMPORT_BYTES = 5 * 1024 * 1024
SESSION_IMPORT_KEY = "pending_user_csv_import"


class UserCsvUploadForm(forms.Form):
    csv_file = forms.FileField(label="CSV-Datei")

    def clean_csv_file(self):
        uploaded = self.cleaned_data["csv_file"]
        if uploaded.size > MAX_IMPORT_BYTES:
            raise forms.ValidationError("Die CSV-Datei darf höchstens 5 MB groß sein.")
        try:
            self.csv_text = uploaded.read().decode("utf-8-sig")
        except UnicodeDecodeError:
            raise forms.ValidationError("Die Datei muss UTF-8-kodiert sein (Excel: CSV UTF-8).")
        if not self.csv_text.strip():
            raise forms.ValidationError("Die CSV-Datei ist leer.")
        return uploaded


def _csv_value(value):
    """Prevent spreadsheet formula execution when opening exported data."""
    value = "" if value is None else str(value)
    if value.startswith(("=", "+", "-", "@", "\t", "\r")):
        return "'" + value
    return value


def export_users_csv(request):
    selected = EXPORT_FIELDS
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="benutzer.csv"'
    response.write("\ufeff")
    writer = csv.writer(response, delimiter=";", lineterminator="\r\n")
    headers = list(selected)
    if "series" in selected:
        headers.append("series_role")
    writer.writerow(headers)

    users = User.objects.select_related("meeting_profile").prefetch_related(
        "groups", "meeting_series_access__series"
    ).order_by("username")
    for user in users:
        assignments = list(user.meeting_series_access.select_related("series").order_by("series__name"))
        rows = assignments or [None]
        for assignment in rows:
            values = {
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "short_description": getattr(getattr(user, "meeting_profile", None), "short_description", ""),
                "is_active": "true" if user.is_active else "false",
                "is_administrator": "true" if (user.is_superuser or user.groups.filter(name="Admin").exists()) else "false",
                "series": assignment.series.name if assignment else "",
                "series_role": assignment.role if assignment else "",
                "date_joined": user.date_joined.isoformat() if user.date_joined else "",
                "last_login": user.last_login.isoformat() if user.last_login else "",
            }
            writer.writerow([_csv_value(values[field]) for field in headers])
    return response


def _resolve_existing_users(grouped):
    """Resolve every CSV account once and reject ambiguous or colliding identities."""
    resolved = {}
    errors = []
    seen_usernames = {}
    seen_emails = {}
    seen_user_ids = {}

    for username, record in grouped:
        normalized_username = username.casefold()
        if normalized_username in seen_usernames and seen_usernames[normalized_username] != username:
            errors.append(
                f"Benutzernamen „{seen_usernames[normalized_username]}“ und „{username}“ "
                "unterscheiden sich nur durch Groß-/Kleinschreibung."
            )
        else:
            seen_usernames[normalized_username] = username

        username_matches = list(User.objects.filter(username__iexact=username)[:2])
        if len(username_matches) > 1:
            errors.append(f"Der vorhandene Benutzername „{username}“ ist nicht eindeutig.")
            continue
        username_user = username_matches[0] if username_matches else None

        email = (record["values"].get("email") or "").strip()
        normalized_email = email.casefold()
        if normalized_email and normalized_email in seen_emails and seen_emails[normalized_email] != username:
            errors.append(
                f"Die E-Mail-Adresse „{email}“ wird mehreren CSV-Benutzern zugeordnet."
            )
            continue
        if normalized_email:
            seen_emails[normalized_email] = username
        email_matches = list(User.objects.filter(email__iexact=email)[:2]) if email else []
        if len(email_matches) > 1:
            errors.append(f"Die E-Mail-Adresse „{email}“ gehört zu mehreren vorhandenen Benutzerkonten.")
            continue
        email_user = email_matches[0] if email_matches else None

        if username_user and email_user and username_user.pk != email_user.pk:
            errors.append(
                f"Benutzer „{username}“: Benutzername und E-Mail-Adresse gehören zu unterschiedlichen Konten."
            )
            continue

        user = email_user or username_user
        if user:
            previous_username = seen_user_ids.get(user.pk)
            if previous_username and previous_username != username:
                errors.append(
                    f"Die CSV-Datensätze „{previous_username}“ und „{username}“ würden dasselbe Benutzerkonto ändern."
                )
                continue
            seen_user_ids[user.pk] = username
            if User.objects.filter(username__iexact=username).exclude(pk=user.pk).exists():
                errors.append(f"Der gewünschte Benutzername „{username}“ ist bereits durch ein anderes Konto belegt.")
                continue
        resolved[username] = user

    return resolved, errors


def _parse_bool(value, field, row_number, errors):
    normalized = (value or "").strip().lower()
    if normalized in {"true", "1", "ja", "yes", "aktiv", "aktiviert"}:
        return True
    if normalized in {"false", "0", "nein", "no", "inaktiv", "deaktiviert"}:
        return False
    errors.append(f"Zeile {row_number}: „{field}“ muss Ja/Nein bzw. true/false sein.")
    return None


def _csv_data_text(text):
    """Ignore explanatory comment lines in documented CSV templates."""
    return "\\n".join(line for line in text.splitlines() if not line.lstrip().startswith("#"))


def _parse_csv(text):
    errors = []
    reader = csv.DictReader(io.StringIO(_csv_data_text(text), newline=""), delimiter=";")
    headers = reader.fieldnames or []
    if not headers:
        return [], ["Die CSV-Datei enthält keine Kopfzeile."]
    unknown = [name for name in headers if name not in ACCEPTED_FIELDS]
    if unknown:
        errors.append("Unbekannte CSV-Spalten: " + ", ".join(unknown))
    if "username" not in headers:
        errors.append("Die Pflichtspalte „username“ fehlt.")
    if "series" in headers and "series_role" not in headers:
        errors.append("Bei Serienzuordnungen ist zusätzlich die Spalte „series_role“ erforderlich.")
    if errors:
        return [], errors

    grouped = OrderedDict()
    series_by_name = {name: pk for pk, name in MeetingSeries.objects.values_list("pk", "name")}
    roles = {
        "participant": SeriesAccess.ROLE_PARTICIPANT,
        "teilnehmer*in": SeriesAccess.ROLE_PARTICIPANT,
        "moderator": SeriesAccess.ROLE_MODERATOR,
        "moderator*in": SeriesAccess.ROLE_MODERATOR,
        "reader": SeriesAccess.ROLE_READER,
        "leser*in": SeriesAccess.ROLE_READER,
    }
    for row_number, raw in enumerate(reader, start=2):
        if None in raw:
            errors.append(f"Zeile {row_number}: Die Zeile enthält mehr Werte als die Kopfzeile.")
            continue
        row = {key: (value or "").strip() for key, value in raw.items() if key}
        username = row.get("username", "")
        if not username:
            errors.append(f"Zeile {row_number}: Benutzername fehlt.")
            continue
        if len(username) > 150:
            errors.append(f"Zeile {row_number}: Benutzername ist länger als 150 Zeichen.")
            continue
        record = grouped.setdefault(username, {"values": {}, "series": [], "row": row_number})
        for field in ("first_name", "last_name", "email", "short_description", "is_active", "is_administrator"):
            if field in headers:
                value = row.get(field, "")
                if field in {"is_active", "is_administrator"}:
                    value = _parse_bool(value, field, row_number, errors)
                if field in record["values"] and record["values"][field] != value:
                    errors.append(f"Zeile {row_number}: Benutzer „{username}“ hat widersprüchliche Werte für „{field}“.")
                else:
                    record["values"][field] = value
        if "series" in headers:
            series_name = row.get("series", "")
            role_name = row.get("series_role", "").lower()
            if series_name:
                if series_name not in series_by_name:
                    errors.append(f"Zeile {row_number}: Besprechungsreihe „{series_name}“ existiert nicht.")
                elif role_name not in roles:
                    errors.append(f"Zeile {row_number}: Unbekannte Serienrolle „{row.get('series_role', '')}“.")
                else:
                    assignment = (series_by_name[series_name], roles[role_name])
                    if assignment in record["series"]:
                        errors.append(f"Zeile {row_number}: Serienzuordnung „{series_name}“ für „{username}“ ist doppelt.")
                    else:
                        record["series"].append(assignment)
    if not grouped:
        errors.append("Die CSV-Datei enthält keine Benutzerdatensätze.")
    return list(grouped.items()), errors


def import_users_csv(request):
    if request.method == "POST" and request.POST.get("action") == "confirm":
        pending = request.session.get(SESSION_IMPORT_KEY)
        if not pending or pending.get("token") != request.POST.get("token"):
            messages.error(request, "Die Importvorschau ist abgelaufen. Bitte lade die CSV-Datei erneut hoch.")
            return redirect("management_user_csv_import") if request.path.startswith("/verwaltung/") else redirect("admin:auth_user_csv_import")
        grouped, errors = _parse_csv(pending["text"])
        resolved_users, identity_errors = _resolve_existing_users(grouped)
        errors.extend(identity_errors)
        if "is_administrator" in pending.get("headers", []) and not (
            request.user.is_superuser or request.user.groups.filter(name="Admin").exists()
        ):
            errors.append("Nur globale Administratoren dürfen die Admin-Rolle per CSV ändern.")
        if errors:
            request.session.pop(SESSION_IMPORT_KEY, None)
            messages.error(request, "Die CSV-Datei ist nicht mehr gültig. Bitte erneut hochladen.")
            return redirect("management_user_csv_import") if request.path.startswith("/verwaltung/") else redirect("admin:auth_user_csv_import")
        created = updated = 0
        with transaction.atomic():
            for username, record in grouped:
                user = resolved_users.get(username)
                was_created = user is None
                if was_created:
                    user = User(username=username)
                    user.set_password(get_random_string(64))
                    created += 1
                else:
                    updated += 1
                # The email may identify an existing account whose username changed.
                # Apply the CSV username after resolving the existing user.
                user.username = username
                for field, value in record["values"].items():
                    if field != "is_administrator":
                        setattr(user, field, value)
                user.save()
                if "short_description" in record["values"]:
                    UserProfile.objects.update_or_create(
                        user=user,
                        defaults={"short_description": record["values"]["short_description"]},
                    )
                if "is_administrator" in record["values"]:
                    sync_admin_access(user, record["values"]["is_administrator"])
                if "series" in pending["headers"]:
                    SeriesAccess.objects.filter(user=user).delete()
                    SeriesAccess.objects.bulk_create([
                        SeriesAccess(user=user, series_id=series_id, role=role)
                        for series_id, role in record["series"]
                    ])
        request.session.pop(SESSION_IMPORT_KEY, None)
        messages.success(
            request,
            f"CSV-Import abgeschlossen: {created} Benutzer neu angelegt, {updated} Benutzer aktualisiert.",
        )
        return redirect("management_users") if request.path.startswith("/verwaltung/") else redirect("admin:auth_user_changelist")

    form = UserCsvUploadForm(request.POST or None, request.FILES or None)
    preview = None
    errors = []
    if request.method == "POST" and form.is_valid():
        text = form.csv_text
        grouped, errors = _parse_csv(text)
        resolved_users, identity_errors = _resolve_existing_users(grouped)
        errors.extend(identity_errors)
        headers = next(csv.reader(io.StringIO(_csv_data_text(text)), delimiter=";"))
        if "is_administrator" in headers and not (
            request.user.is_superuser or request.user.groups.filter(name="Admin").exists()
        ):
            errors.append("Nur globale Administratoren dürfen die Admin-Rolle per CSV ändern.")
        if not errors:
            token = secrets.token_urlsafe(18)
            request.session[SESSION_IMPORT_KEY] = {
                "token": token,
                "text": text,
                "headers": next(csv.reader(io.StringIO(text), delimiter=";")),
            }
            preview = {
                "token": token,
                "users": len(grouped),
                "new_users": sum(resolved_users.get(username) is None for username, record in grouped),
                "updated_users": sum(resolved_users.get(username) is not None for username, record in grouped),
                "assignments": sum(len(record["series"]) for _, record in grouped),
            }
    return render(request, "meetings/management_user_csv_import.html" if request.path.startswith("/verwaltung/") else "admin/auth/user/csv_import.html", {
        **admin.site.each_context(request),
        "form": form, "preview": preview, "errors": errors,
        "title": "Benutzer per CSV importieren",
        "opts": User._meta,
    })
