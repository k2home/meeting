import csv
import io
import secrets
from datetime import datetime

from django import forms
from django.contrib import admin, messages
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import redirect, render

from .models import AgendaItem, Meeting, MeetingSeries, Topic, UserProfile
from django.contrib.auth import get_user_model

User = get_user_model()

CSV_FIELDS = (
    "series", "topic_series", "meeting_date", "meeting_title", "topic_title", "topic_current_status",
    "topic_status", "responsible_username", "responsible_kurzbezeichnung",
    "agenda_responsible_username", "agenda_responsible_kurzbezeichnung", "agenda_text",
)
LEGACY_FIELDS = ("topic_due_date",)
REQUIRED_FIELDS = ("series", "meeting_date", "topic_title")
MAX_IMPORT_BYTES = 5 * 1024 * 1024
SESSION_KEY = "pending_topic_agenda_csv_import"
STATUS_VALUES = {value for value, _ in AgendaItem.STATUS}


class TopicAgendaCsvUploadForm(forms.Form):
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


def sample_csv_response():
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="muster_themen_und_punkte.csv"'
    response.write("\ufeff")
    writer = csv.writer(response, delimiter=";", lineterminator="\r\n")
    writer.writerow(CSV_FIELDS)
    writer.writerow(["Lenkungskreis Digitalisierung", "Lenkungskreis Digitalisierung", "2026-12-03", "Einführung der E-Akte", "Projektstand und offene technische Fragen", "in_progress", "m.mustermann", "", "", "", "Sachstand der Pilotierung vorstellen; offene Schnittstellen klären."])
    writer.writerow(["Lenkungskreis Digitalisierung", "Lenkungskreis Digitalisierung", "2027-01-14", "Einführung der E-Akte", "Projektstand und offene technische Fragen", "in_progress", "m.mustermann", "", "a.beispiel", "", "Rückmeldung aus den Pilotbereichen auswerten."])
    writer.writerow(["Lenkungskreis Digitalisierung", "Lenkungskreis Digitalisierung", "2026-12-03", "Reguläre Sitzung", "Schulungsplanung", "Konzept und Zeitplan für die Beschäftigtenschulungen", "open", "a.beispiel", "", "", "", "Vorschlag für Schulungsformate und Termine abstimmen."])
    _write_csv_documentation(writer)
    return response


def _write_csv_documentation(writer):
    writer.writerow([])
    writer.writerow(["# GÜLTIGE WERTE", "Feld", "Erlaubte Werte"])
    writer.writerow(["#", "series", "Besprechungsreihe des konkreten Termins; legt Meeting fest."])
    writer.writerow(["#", "topic_series", "Zuständige Besprechungsreihe des Themas; leer bedeutet ohne Zuordnung. Bei alten Dateien ohne diese Spalte wird series übernommen."])
    writer.writerow(["#", "topic_status", "; ".join(f"{value} ({label})" for value, label in AgendaItem.STATUS)])
    writer.writerow(["#", "responsible_username / responsible_kurzbezeichnung", "Legacy-Spalte; wird beim Import nicht mehr als Themenzuständigkeit gespeichert."])
    writer.writerow(["#", "agenda_responsible_username / agenda_responsible_kurzbezeichnung", "Optionale abweichende Person für genau diesen Tagesordnungspunkt; leer bedeutet Hauptverantwortliche Person."])
    writer.writerow([])
    writer.writerow(["# DATUMS-/FORMATVORGABEN", "Feld", "Format"])
    writer.writerow(["#", "meeting_date", "yyyy-mm-dd (z. B. 2026-12-03); das Datum gehört zum Besprechungstermin."])
    writer.writerow(["#", "CSV-Trennzeichen", "Semikolon (;)"])
    writer.writerow(["#", "Zeichencodierung", "UTF-8"])
    writer.writerow(["#", "Kompatibilität", "Alte Dateien mit topic_due_date werden weiterhin eingelesen; abweichende Wiedervorlagen werden als eigener Tagesordnungspunkt angelegt."])


def _profile_short_description(user):
    if not user:
        return ""
    profile = getattr(user, "meeting_profile", None)
    return profile.short_description if profile else ""


def export_topic_agenda_csv(request):
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="themen_und_punkte_export.csv"'
    response.write("\ufeff")
    writer = csv.writer(response, delimiter=";", lineterminator="\r\n")
    writer.writerow(CSV_FIELDS)
    items = AgendaItem.objects.select_related(
        "meeting__series", "topic", "topic__series", "assigned_to"
    ).order_by("meeting__date", "meeting__series__name", "position", "pk")
    for item in items:
        meeting, topic = item.meeting, item.topic
        writer.writerow([
            meeting.series.name if meeting.series else "",
            topic.series.name if topic.series else "",
            meeting.date.isoformat(),
            meeting.title,
            topic.title,
            topic.description,
            item.status,
            "",
            "",
            item.assigned_to.username if item.assigned_to else "",
            _profile_short_description(item.assigned_to),
            item.working_text,
        ])
    _write_csv_documentation(writer)
    return response


def _parse_date(value, field, row_number, errors, required=False):
    value = (value or "").strip()
    if not value:
        if required:
            errors.append(f"Zeile {row_number}: „{field}“ fehlt.")
        return None
    for fmt in ("%Y-%m-%d", "%d.%m.%Y"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            pass
    errors.append(f"Zeile {row_number}: „{field}“ muss JJJJ-MM-TT oder TT.MM.JJJJ sein.")
    return None


def _resolve_user(username, short_description, row_number, label, errors):
    user = User.objects.filter(username=username).first() if username else None
    if username and user is None:
        errors.append(f"Zeile {row_number}: {label} mit Anmeldename „{username}“ existiert nicht.")
    if short_description:
        profiles = list(UserProfile.objects.filter(
            short_description__iexact=short_description
        ).select_related("user")[:2])
        if not profiles:
            errors.append(f"Zeile {row_number}: Keine Person mit Kurzbezeichnung „{short_description}“ gefunden.")
        elif len(profiles) > 1:
            errors.append(f"Zeile {row_number}: Die Kurzbezeichnung „{short_description}“ ist nicht eindeutig.")
        else:
            short_user = profiles[0].user
            if user and user.pk != short_user.pk:
                errors.append(f"Zeile {row_number}: Anmeldename und Kurzbezeichnung für {label} gehören zu unterschiedlichen Personen.")
            else:
                user = short_user
    return user


def parse_topic_agenda_csv(text):
    errors = []
    reader = csv.DictReader(io.StringIO(text, newline=""), delimiter=";")
    headers = reader.fieldnames or []
    if not headers:
        return [], ["Die CSV-Datei enthält keine Kopfzeile."]
    missing = [field for field in REQUIRED_FIELDS if field not in headers]
    unknown = [field for field in headers if field not in CSV_FIELDS and field not in LEGACY_FIELDS]
    if missing:
        errors.append("Pflichtspalten fehlen: " + ", ".join(missing))
    if unknown:
        errors.append("Unbekannte CSV-Spalten: " + ", ".join(unknown))
    if errors:
        return [], errors

    series_by_name = {name: pk for pk, name in MeetingSeries.objects.values_list("pk", "name")}
    rows, topic_records, seen, positions = [], {}, set(), {}
    legacy_followups = []
    for row_number, raw in enumerate(reader, start=2):
        if None in raw:
            errors.append(f"Zeile {row_number}: Die Zeile enthält mehr Werte als die Kopfzeile.")
            continue
        row = {key: (value or "").strip() for key, value in raw.items() if key}
        if not any(row.values()) or (row.get("series") or "").startswith("#"):
            continue
        series_name = row.get("series", "")
        series_id = series_by_name.get(series_name)
        if not series_id:
            errors.append(f"Zeile {row_number}: Besprechungsreihe „{series_name}“ existiert nicht.")
            continue
        if "topic_series" in headers:
            topic_series_name = row.get("topic_series", "")
            topic_series_id = series_by_name.get(topic_series_name) if topic_series_name else None
            if topic_series_name and topic_series_id is None:
                errors.append(f"Zeile {row_number}: Zuständige Themenreihe „{topic_series_name}“ existiert nicht.")
                continue
        else:
            # Legacy CSV files used one series column for both the meeting and topic.
            topic_series_id = series_id

        meeting_date = _parse_date(row.get("meeting_date"), "meeting_date", row_number, errors, True)
        legacy_due_date = _parse_date(row.get("topic_due_date"), "topic_due_date", row_number, errors) if "topic_due_date" in headers else None
        title = row.get("topic_title", "")
        meeting_title = row.get("meeting_title", "")
        if not title:
            errors.append(f"Zeile {row_number}: topic_title fehlt.")
        if len(title) > 240:
            errors.append(f"Zeile {row_number}: topic_title ist länger als 240 Zeichen.")
        if len(meeting_title) > 180:
            errors.append(f"Zeile {row_number}: meeting_title ist länger als 180 Zeichen.")
        status = row.get("topic_status") or "open"
        if status not in STATUS_VALUES:
            errors.append(f"Zeile {row_number}: Unbekannter topic_status „{status}“.")

        main_user = _resolve_user(
            row.get("responsible_username", ""), row.get("responsible_kurzbezeichnung", ""),
            row_number, "Legacy-Zuständigkeit", errors,
        )
        agenda_user = _resolve_user(
            row.get("agenda_responsible_username", ""), row.get("agenda_responsible_kurzbezeichnung", ""),
            row_number, "Verantwortliche Person des Tagesordnungspunkts", errors,
        )
        agenda_user = agenda_user or main_user
        if not meeting_date or not title:
            continue

        topic_key = "{}:{}".format(topic_series_id if topic_series_id is not None else "none", title.casefold())
        topic_data = {"series_id": topic_series_id, "title": title, "description": row.get("topic_current_status", "")}
        if topic_key not in topic_records:
            topic_records[topic_key] = {"topic": topic_data, "row": row_number}

        schedule_rows = [(meeting_date, row.get("agenda_text", ""), agenda_user.pk if agenda_user else None)]
        # Defer synthetic legacy appointments until all explicit CSV rows have
        # been read, so a real row for the same future meeting takes precedence.
        if legacy_due_date and legacy_due_date != meeting_date:
            legacy_followups.append({
                "row_number": row_number, "series_id": series_id,
                "meeting_date": legacy_due_date, "meeting_title": meeting_title,
                "topic_key": topic_key, "topic": topic_data,
            })

        for scheduled_date, agenda_text, agenda_assignee_id in schedule_rows:
            schedule_key = (series_id, scheduled_date, topic_key)
            if schedule_key in seen:
                continue
            seen.add(schedule_key)
            meeting_key = (series_id, scheduled_date)
            position = positions.get(meeting_key, 0)
            positions[meeting_key] = position + 1
            rows.append({
                "row_number": row_number, "series_id": series_id, "meeting_date": scheduled_date,
                "meeting_title": meeting_title, "topic_key": topic_key, "topic": topic_data,
                "agenda_text": agenda_text, "agenda_assigned_to_id": agenda_assignee_id,
                "agenda_status": status,
                "position": position,
            })

    for followup in legacy_followups:
        schedule_key = (followup["series_id"], followup["meeting_date"], followup["topic_key"])
        if schedule_key in seen:
            continue
        seen.add(schedule_key)
        meeting_key = (followup["series_id"], followup["meeting_date"])
        position = positions.get(meeting_key, 0)
        positions[meeting_key] = position + 1
        rows.append({
            **followup,
            "agenda_text": "",
            "agenda_assigned_to_id": None,
            "agenda_status": followup["topic"].get("status", "open"),
            "position": position,
        })

    if not rows:
        errors.append("Die CSV-Datei enthält keine gültigen Datensätze.")
    if errors:
        return [], errors

    for row in rows:
        meeting = Meeting.objects.filter(series_id=row["series_id"], date=row["meeting_date"]).first()
        if meeting and (meeting.finalized_at or meeting.snapshots.exists()):
            errors.append(f"Zeile {row['row_number']}: Der Termin am {row['meeting_date']:%d.%m.%Y} ist abgeschlossen und kann nicht importiert werden.")
        row["existing_meeting_id"] = meeting.pk if meeting else None
    for record in topic_records.values():
        data = record["topic"]
        matches = Topic.objects.filter(series_id=data["series_id"], title=data["title"])
        if matches.count() > 1:
            errors.append(f"Zeile {record['row']}: Thema „{data['title']}“ ist mehrfach vorhanden.")
        record["existing_topic_id"] = matches.first().pk if matches.exists() else None
    if errors:
        return [], errors
    return rows, []


def _preview(rows, topic_ids):
    topics = {row["topic_key"] for row in rows}
    existing_topics = {key for key in topics if topic_ids.get(key)}
    new_topics = topics - existing_topics
    new_meetings = {
        (row["series_id"], row["meeting_date"]) for row in rows if row["existing_meeting_id"] is None
    }
    return {
        "rows": len(rows), "topics": len(topics), "meetings": len(new_meetings),
        "agenda_items": len(rows), "new_topics": len(new_topics),
        "existing_topics": len(existing_topics),
    }


def import_topic_agenda_csv(request):
    if request.method == "POST" and request.POST.get("action") == "confirm":
        pending = request.session.get(SESSION_KEY)
        if not pending or pending.get("token") != request.POST.get("token"):
            messages.error(request, "Die Importvorschau ist abgelaufen. Bitte lade die CSV-Datei erneut hoch.")
            return redirect("admin:meetings_topic_csv_import")
        rows, errors = parse_topic_agenda_csv(pending["text"])
        if errors:
            request.session.pop(SESSION_KEY, None)
            messages.error(request, "Die CSV-Datei ist nicht mehr gültig: " + " ".join(errors[:3]))
            return redirect("admin:meetings_topic_csv_import")

        topic_records = {}
        created_topics = updated_topics = created_meetings = created_items = updated_items = 0
        with transaction.atomic():
            for row in rows:
                key = row["topic_key"]
                if key not in topic_records:
                    data = row["topic"]
                    existing_id = pending["topic_ids"].get(key)
                    topic = Topic.objects.select_for_update().get(pk=existing_id) if existing_id else Topic()
                    if existing_id:
                        updated_topics += 1
                    else:
                        created_topics += 1
                    topic.series_id = data["series_id"]
                    topic.title = data["title"]
                    if data["description"]:
                        topic.description = data["description"]
                    topic.save()
                    topic_records[key] = topic

                meeting = Meeting.objects.filter(series_id=row["series_id"], date=row["meeting_date"]).first()
                if meeting is None:
                    meeting = Meeting.objects.create(
                        series_id=row["series_id"], date=row["meeting_date"], title=row["meeting_title"],
                    )
                    created_meetings += 1
                _, created = AgendaItem.objects.update_or_create(
                    meeting=meeting, topic=topic_records[key],
                    defaults={
                        "working_text": row["agenda_text"],
                        "assigned_to_id": row["agenda_assigned_to_id"],
                        "status": row["agenda_status"],
                        "position": row["position"],
                        "carried_forward": AgendaItem.objects.filter(
                            topic=topic_records[key], meeting__series_id=row["series_id"],
                            meeting__date__lt=row["meeting_date"],
                        ).exists(),
                    },
                )
                if created:
                    created_items += 1
                else:
                    updated_items += 1
        request.session.pop(SESSION_KEY, None)
        messages.success(
            request,
            f"Import abgeschlossen: {created_topics} Themen neu angelegt, {updated_topics} aktualisiert, "
            f"{created_meetings} Termine angelegt, {created_items} Tagesordnungspunkte angelegt und "
            f"{updated_items} aktualisiert.",
        )
        return redirect("admin:meetings_topic_changelist")

    form = TopicAgendaCsvUploadForm(request.POST or None, request.FILES or None)
    preview = None
    errors = []
    if request.method == "POST" and form.is_valid():
        rows, errors = parse_topic_agenda_csv(form.csv_text)
        if not errors:
            topic_ids = {}
            for row in rows:
                key = row["topic_key"]
                if key not in topic_ids:
                    matches = Topic.objects.filter(series_id=row["topic"]["series_id"], title=row["topic"]["title"])
                    topic_ids[key] = matches.first().pk if matches.exists() else None
            token = secrets.token_urlsafe(18)
            request.session[SESSION_KEY] = {"token": token, "text": form.csv_text, "topic_ids": topic_ids}
            preview = {**_preview(rows, topic_ids), "token": token}
    return render(request, "admin/meetings/topic_csv_import.html", {
        **admin.site.each_context(request), "form": form, "preview": preview,
        "errors": errors, "title": "Themen und Tagesordnungspunkte importieren",
        "opts": Topic._meta,
    })
