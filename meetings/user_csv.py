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

User = get_user_model()

EXPORT_FIELDS = (
    "username", "first_name", "last_name", "email", "short_description",
    "is_active", "is_administrator", "series",
)
IMPORT_FIELDS = (
    "username", "first_name", "last_name", "email", "short_description",
    "is_active", "series", "series_role",
)
ACCEPTED_FIELDS = IMPORT_FIELDS + ("is_administrator",)
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
                "is_administrator": "true" if user.groups.filter(name="Admin").exists() else "false",
                "series": assignment.series.name if assignment else "",
                "series_role": assignment.role if assignment else "",
                "date_joined": user.date_joined.isoformat() if user.date_joined else "",
                "last_login": user.last_login.isoformat() if user.last_login else "",
            }
            writer.writerow([_csv_value(values[field]) for field in headers])
    return response


def _find_existing_user(username, values):
    email = values.get("email", "")
    if email:
        matches = User.objects.filter(email__iexact=email)
        if matches.count() == 1:
            return matches.first()
    return User.objects.filter(username=username).first()


def _parse_bool(value, field, row_number, errors):
    normalized = (value or "").strip().lower()
    if normalized in {"true", "1", "ja", "yes", "aktiv", "aktiviert"}:
        return True
    if normalized in {"false", "0", "nein", "no", "inaktiv", "deaktiviert"}:
        return False
    errors.append(f"Zeile {row_number}: „{field}“ muss Ja/Nein bzw. true/false sein.")
    return None


def _parse_csv(text):
    errors = []
    reader = csv.DictReader(io.StringIO(text, newline=""), delimiter=";")
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
            return redirect("admin:auth_user_csv_import")
        grouped, errors = _parse_csv(pending["text"])
        if "is_administrator" in pending.get("headers", []) and not (
            request.user.is_superuser or request.user.groups.filter(name="Admin").exists()
        ):
            errors.append("Nur globale Administratoren dürfen die Admin-Rolle per CSV ändern.")
        if errors:
            request.session.pop(SESSION_IMPORT_KEY, None)
            messages.error(request, "Die CSV-Datei ist nicht mehr gültig. Bitte erneut hochladen.")
            return redirect("admin:auth_user_csv_import")
        created = updated = 0
        with transaction.atomic():
            for username, record in grouped:
                user = _find_existing_user(username, record["values"])
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
                    from django.contrib.auth.models import Group
                    admin_group, _ = Group.objects.get_or_create(name="Admin")
                    if record["values"]["is_administrator"]:
                        user.groups.add(admin_group)
                    else:
                        user.groups.remove(admin_group)
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
        return redirect("admin:auth_user_changelist")

    form = UserCsvUploadForm(request.POST or None, request.FILES or None)
    preview = None
    errors = []
    if request.method == "POST" and form.is_valid():
        text = form.csv_text
        grouped, errors = _parse_csv(text)
        headers = next(csv.reader(io.StringIO(text), delimiter=";"))
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
                "new_users": sum(_find_existing_user(username, record["values"]) is None for username, record in grouped),
                "updated_users": sum(_find_existing_user(username, record["values"]) is not None for username, record in grouped),
                "assignments": sum(len(record["series"]) for _, record in grouped),
            }
    return render(request, "admin/auth/user/csv_import.html", {
        **admin.site.each_context(request),
        "form": form, "preview": preview, "errors": errors,
        "title": "Benutzer per CSV importieren",
        "opts": User._meta,
    })
