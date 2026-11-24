import csv
import io
import secrets
from datetime import datetime

from django import forms
from django.contrib import admin, messages
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils import formats, timezone

from .models import AgendaItem, Meeting, MeetingSeries, Topic, UserProfile
from django.contrib.auth import get_user_model

User = get_user_model()

CSV_FIELDS = (
    "record_type", "series", "topic_series", "meeting_date", "meeting_title", "topic_title",
    "topic_status", "archive_previous_status", "agenda_status", "responsible_username", "responsible_kurzbezeichnung",
    "agenda_responsible_username", "agenda_responsible_kurzbezeichnung", "agenda_text",
    "followup_series", "followup_meeting_date",
)
LEGACY_FIELDS = ("topic_due_date",)
REQUIRED_FIELDS = ("topic_title",)
MAX_IMPORT_BYTES = 5 * 1024 * 1024
SESSION_KEY = "pending_topic_agenda_csv_import"
TOPIC_STATUS_VALUES = {value for value, _ in Topic.STATUS}
AGENDA_STATUS_VALUES = {value for value, _ in AgendaItem.STATUS}


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
    writer.writerow(["agenda", "Lenkungskreis Digitalisierung", "Lenkungskreis Digitalisierung", "2026-12-03", "Einführung der E-Akte", "Projektstand und offene technische Fragen", "open", "", "in_progress", "m.mustermann", "", "", "", "Sachstand der Pilotierung vorstellen; offene Schnittstellen klären.", "", ""])
    writer.writerow(["agenda", "Lenkungskreis Digitalisierung", "Lenkungskreis Digitalisierung", "2027-01-14", "Einführung der E-Akte", "Projektstand und offene technische Fragen", "open", "", "in_progress", "m.mustermann", "", "a.beispiel", "", "Rückmeldung aus den Pilotbereichen auswerten.", "Lenkungskreis Digitalisierung", "2026-12-03"])
    writer.writerow(["agenda", "Lenkungskreis Digitalisierung", "Lenkungskreis Digitalisierung", "2026-12-03", "Reguläre Sitzung", "Schulungsplanung", "open", "", "open", "a.beispiel", "", "", "", "Vorschlag für Schulungsformate und Termine abstimmen.", "", ""])
    _write_csv_documentation(writer)
    return response


def _write_csv_documentation(writer):
    writer.writerow([])
    writer.writerow(["# GÜLTIGE WERTE", "Feld", "Erlaubte Werte"])
    writer.writerow(["#", "record_type", "agenda = Tagesordnungspunkt; topic = Thema ohne Tagesordnungspunkt. Fehlt die Spalte, wird agenda angenommen."])
    writer.writerow(["#", "series", "Besprechungsreihe des konkreten Termins; bei record_type=topic optional."])
    writer.writerow(["#", "topic_series", "Zuständige Besprechungsreihe des Themas; leer bedeutet ohne Zuordnung. Bei alten Dateien ohne diese Spalte wird series übernommen."])
    writer.writerow(["#", "topic_status", "; ".join(f"{value} ({label})" for value, label in Topic.STATUS)])
    writer.writerow(["#", "archive_previous_status", "Vorheriger Themenstatus (open, in_progress oder done); bei älteren CSV-Dateien wird open angenommen. Archivierte Themen werden als Themen-Datensatz ohne aktive Tagesordnung exportiert."])
    writer.writerow(["#", "agenda_status", "; ".join(f"{value} ({label})" for value, label in AgendaItem.STATUS)])
    writer.writerow(["#", "responsible_username / responsible_kurzbezeichnung", "Optionale Hauptzuständigkeit des Themas."])
    writer.writerow(["#", "agenda_responsible_username / agenda_responsible_kurzbezeichnung", "Optionale abweichende Person für genau diesen Tagesordnungspunkt; leer bedeutet Hauptverantwortliche Person."])
    writer.writerow(["#", "followup_series / followup_meeting_date", "Besprechungsreihe und Datum des Quell-Tagesordnungspunkts einer Wiedervorlage; beide Felder gemeinsam ausfüllen."])
    writer.writerow([])
    writer.writerow(["# DATUMS-/FORMATVORGABEN", "Feld", "Format"])
    writer.writerow(["#", "meeting_date", "yyyy-mm-dd (z. B. 2026-12-03); das Datum gehört zum Besprechungstermin."])
    writer.writerow(["#", "CSV-Trennzeichen", "Semikolon (;)"])
    writer.writerow(["#", "Zeichencodierung", "UTF-8"])
    writer.writerow(["#", "Kompatibilität", "Alte Dateien mit topic_due_date werden weiterhin eingelesen; abweichende Wiedervorlagen werden als eigener Tagesordnungspunkt angelegt."])


def _csv_value(value):
    """Neutralize spreadsheet formulas in exported user-controlled cells."""
    value = "" if value is None else str(value)
    if value.startswith(("=", "+", "-", "@", "\t", "\r")):
        return "'" + value
    return value


def _profile_short_description(user):
    if not user:
        return ""
    profile = getattr(user, "meeting_profile", None)
    return profile.short_description if profile else ""


def export_topic_agenda_csv(request, allowed_series_ids=None):
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="themen_und_punkte_export.csv"'
    response["Cache-Control"] = "private, no-store"
    response.write("\ufeff")
    writer = csv.writer(response, delimiter=";", lineterminator="\r\n")
    writer.writerow(CSV_FIELDS)
    items = AgendaItem.objects.exclude(topic__status="archived").select_related(
        "meeting__series", "topic", "topic__series", "topic__assigned_to", "assigned_to"
    ).order_by("meeting__date", "meeting__series__name", "position", "pk")
    if allowed_series_ids is not None:
        items = items.filter(
            meeting__series_id__in=allowed_series_ids,
            topic__series_id__in=allowed_series_ids,
        )
    for item in items:
        meeting, topic = item.meeting, item.topic
        source = item.followup_of
        writer.writerow([_csv_value(value) for value in [
            "agenda",
            meeting.series.name if meeting.series else "",
            topic.series.name if topic.series else "",
            meeting.date.isoformat(),
            meeting.title,
            topic.title,
            topic.status,
            "",
            item.status,
            topic.assigned_to.username if topic.assigned_to else "",
            _profile_short_description(topic.assigned_to),
            item.assigned_to.username if item.assigned_to else "",
            _profile_short_description(item.assigned_to),
            item.working_text,
            source.meeting.series.name if source and source.meeting.series else "",
            source.meeting.date.isoformat() if source else "",
        ]])
    topics_without_agenda = (
        Topic.objects.filter(status="archived") | Topic.objects.filter(agenda_items__isnull=True)
    ).select_related("series", "assigned_to").order_by("title", "pk")
    if allowed_series_ids is not None:
        topics_without_agenda = topics_without_agenda.filter(series_id__in=allowed_series_ids)
    for topic in topics_without_agenda:
        writer.writerow([_csv_value(value) for value in [
            "topic", topic.series.name if topic.series else "", topic.series.name if topic.series else "",
            "", "", topic.title, topic.status, topic.archive_previous_status, "",
            topic.assigned_to.username if topic.assigned_to else "",
            _profile_short_description(topic.assigned_to), "", "", "", "", "",
        ]])
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
        if not any(row.values()) or (row.get("record_type") or "").startswith("#") or (row.get("series") or "").startswith("#"):
            continue
        record_type = (row.get("record_type") or "agenda").lower()
        if record_type not in {"agenda", "topic"}:
            errors.append(f"Zeile {row_number}: Unbekannter record_type „{record_type}“.")
            continue
        series_name = row.get("series", "")
        series_id = series_by_name.get(series_name) if series_name else None
        if record_type == "agenda" and series_id is None:
            errors.append(f"Zeile {row_number}: Besprechungsreihe „{series_name}“ existiert nicht.")
            continue
        if "topic_series" in headers:
            topic_series_name = row.get("topic_series", "")
            topic_series_id = series_by_name.get(topic_series_name) if topic_series_name else None
            if topic_series_name and topic_series_id is None:
                errors.append(f"Zeile {row_number}: Zuständige Themenreihe „{topic_series_name}“ existiert nicht.")
                continue
        else:
            topic_series_id = series_id

        meeting_date = _parse_date(row.get("meeting_date"), "meeting_date", row_number, errors, record_type == "agenda")
        legacy_due_date = _parse_date(row.get("topic_due_date"), "topic_due_date", row_number, errors) if record_type == "agenda" and "topic_due_date" in headers else None
        title = row.get("topic_title", "")
        meeting_title = row.get("meeting_title", "")
        if not title:
            errors.append(f"Zeile {row_number}: topic_title fehlt.")
        if len(title) > 240:
            errors.append(f"Zeile {row_number}: topic_title ist länger als 240 Zeichen.")
        if len(meeting_title) > 180:
            errors.append(f"Zeile {row_number}: meeting_title ist länger als 180 Zeichen.")
        # In älteren CSV-Dateien bezeichnet topic_status den Punktstatus. Ohne
        # agenda_status darf deshalb der eigenständige Themenstatus nicht geändert werden.
        topic_status = (row.get("topic_status") or "open") if "agenda_status" in headers else None
        if topic_status is not None and topic_status not in TOPIC_STATUS_VALUES:
            errors.append(f"Zeile {row_number}: Unbekannter topic_status „{topic_status}“.")
        archive_previous_status = row.get("archive_previous_status", "").strip()
        if archive_previous_status and archive_previous_status not in {"open", "in_progress", "done"}:
            errors.append(f"Zeile {row_number}: Unbekannter archive_previous_status „{archive_previous_status}“.")
        if topic_status == "archived":
            if record_type != "topic":
                errors.append(f"Zeile {row_number}: Archivierte Themen dürfen nicht als Tagesordnungspunkt importiert werden; verwende record_type=topic.")
            if not archive_previous_status:
                archive_previous_status = "open"
        agenda_status = (row.get("agenda_status") if "agenda_status" in headers else row.get("topic_status")) or "open"
        if agenda_status not in AGENDA_STATUS_VALUES:
            errors.append(f"Zeile {row_number}: Unbekannter agenda_status „{agenda_status}“.")

        main_user = _resolve_user(
            row.get("responsible_username", ""), row.get("responsible_kurzbezeichnung", ""),
            row_number, "Legacy-Zuständigkeit", errors,
        )
        agenda_user = _resolve_user(
            row.get("agenda_responsible_username", ""), row.get("agenda_responsible_kurzbezeichnung", ""),
            row_number, "Verantwortliche Person des Tagesordnungspunkts", errors,
        )
        agenda_user = agenda_user or main_user
        if (record_type == "agenda" and not meeting_date) or not title:
            continue

        topic_key = "{}:{}".format(topic_series_id if topic_series_id is not None else "none", title.casefold())
        topic_data = {"series_id": topic_series_id, "title": title}
        if "topic_status" in headers and "agenda_status" in headers:
            topic_data["status"] = topic_status
            if topic_status == "archived":
                topic_data["archive_previous_status"] = archive_previous_status
        if "responsible_username" in headers or "responsible_kurzbezeichnung" in headers:
            topic_data["assigned_to_id"] = main_user.pk if main_user else None
        if topic_key not in topic_records:
            topic_records[topic_key] = {"topic": topic_data.copy(), "row": row_number}
        else:
            existing_data = topic_records[topic_key]["topic"]
            for field, value in topic_data.items():
                if field in existing_data and existing_data[field] != value:
                    errors.append(f"Zeile {row_number}: Das Thema „{title}“ hat widersprüchliche Werte für „{field}“ in mehreren CSV-Zeilen.")
                else:
                    existing_data[field] = value

        if record_type == "topic":
            rows.append({"record_type": "topic", "row_number": row_number, "topic_key": topic_key, "topic": topic_data})
            continue
        followup_series_name = row.get("followup_series", "")
        followup_date = _parse_date(row.get("followup_meeting_date"), "followup_meeting_date", row_number, errors) if row.get("followup_meeting_date") else None
        followup_series_id = series_by_name.get(followup_series_name) if followup_series_name else None
        if followup_series_name and followup_series_id is None:
            errors.append(f"Zeile {row_number}: Wiedervorlage-Besprechungsreihe „{followup_series_name}“ existiert nicht.")
        if bool(followup_series_name) != bool(followup_date):
            errors.append(f"Zeile {row_number}: followup_series und followup_meeting_date müssen gemeinsam ausgefüllt sein.")
        schedule_rows = [(meeting_date, row.get("agenda_text", ""), agenda_user.pk if agenda_user else None)]
        # Defer synthetic legacy appointments until all explicit CSV rows have
        # been read, so a real row for the same future meeting takes precedence.
        if legacy_due_date and legacy_due_date != meeting_date:
            legacy_followups.append({
                "row_number": row_number, "series_id": series_id,
                "meeting_date": legacy_due_date, "meeting_title": meeting_title,
                "topic_key": topic_key, "topic": topic_data,
                "agenda_status": agenda_status,
                "agenda_text_present": True,
                "agenda_assignment_present": True,
                "agenda_status_present": True,
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
                "record_type": "agenda", "row_number": row_number, "series_id": series_id, "meeting_date": scheduled_date,
                "meeting_title": meeting_title, "topic_key": topic_key, "topic": topic_data,
                "agenda_text": agenda_text, "agenda_assigned_to_id": agenda_assignee_id,
                "agenda_status": agenda_status,
                "agenda_text_present": "agenda_text" in headers,
                "agenda_assignment_present": ("agenda_responsible_username" in headers or "agenda_responsible_kurzbezeichnung" in headers),
                "agenda_status_present": ("agenda_status" in headers or "topic_status" in headers),
                "followup_series_id": followup_series_id, "followup_meeting_date": followup_date,
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
            "agenda_status": followup["agenda_status"],
            "agenda_text_present": True, "agenda_assignment_present": True, "agenda_status_present": True,
            "record_type": "agenda", "followup_series_id": None, "followup_meeting_date": None,
            "position": position,
        })

    if not rows:
        errors.append("Die CSV-Datei enthält keine gültigen Datensätze.")
    if errors:
        return [], errors

    agenda_source_keys = {
        (row["series_id"], row["meeting_date"], row["topic_key"])
        for row in rows if row.get("record_type") != "topic"
    }
    for row in rows:
        if row.get("record_type") == "topic":
            row["existing_meeting_id"] = None
            continue
        if row.get("followup_series_id"):
            source_key = (row["followup_series_id"], row["followup_meeting_date"], row["topic_key"])
            existing_topic = Topic.objects.filter(
                series_id=row["topic"]["series_id"], title__iexact=row["topic"]["title"]
            ).first()
            source_in_database = bool(existing_topic and AgendaItem.objects.filter(
                topic=existing_topic, meeting__series_id=row["followup_series_id"],
                meeting__date=row["followup_meeting_date"],
            ).exists())
            if source_key == (row["series_id"], row["meeting_date"], row["topic_key"]):
                errors.append(f"Zeile {row['row_number']}: Ein Tagesordnungspunkt kann nicht auf sich selbst verweisen.")
            if source_key not in agenda_source_keys and not source_in_database:
                errors.append(f"Zeile {row['row_number']}: Der Quell-Tagesordnungspunkt für die Wiedervorlage existiert nicht.")
            if existing_topic:
                source_item = AgendaItem.objects.filter(
                    topic=existing_topic, meeting__series_id=row["followup_series_id"],
                    meeting__date=row["followup_meeting_date"],
                ).first()
                if source_item and AgendaItem.objects.filter(followup_of=source_item).exclude(
                    meeting__series_id=row["series_id"], meeting__date=row["meeting_date"]
                ).exists():
                    errors.append(f"Zeile {row['row_number']}: Für den Quell-Tagesordnungspunkt existiert bereits eine andere Wiedervorlage.")
        meeting = Meeting.objects.filter(series_id=row["series_id"], date=row["meeting_date"]).first()
        if meeting and (meeting.finalized_at or meeting.snapshots.exists()):
            errors.append(f"Zeile {row['row_number']}: Der Termin am {formats.date_format(row['meeting_date'], 'DATE_FORMAT')} ist abgeschlossen und kann nicht importiert werden.")
        row["existing_meeting_id"] = meeting.pk if meeting else None
    for topic_key, record in topic_records.items():
        data = record["topic"]
        matches = Topic.objects.filter(series_id=data["series_id"], title__iexact=data["title"])
        if matches.count() > 1:
            errors.append(f"Zeile {record['row']}: Thema „{data['title']}“ ist mehrfach vorhanden.")
        existing_topic = matches.first() if matches.exists() else None
        record["existing_topic_id"] = existing_topic.pk if existing_topic else None
        effective_status = data.get("status", existing_topic.status if existing_topic else "open")
        has_agenda_rows = any(
            row.get("record_type") != "topic" and row.get("topic_key") == topic_key
            for row in rows
        )
        if (effective_status == "archived" or (existing_topic and existing_topic.status == "archived")) and has_agenda_rows:
            errors.append(f"Zeile {record['row']}: Das archivierte Thema „{data['title']}“ muss zuerst über die Themenansicht wieder geöffnet werden, bevor Tagesordnungspunkte importiert werden können.")
        if effective_status == "archived" and existing_topic and existing_topic.agenda_items.filter(
            meeting__finalized_at__isnull=True,
        ).exists():
            errors.append(
                f"Zeile {record['row']}: Thema „{data['title']}“ kann nicht archiviert werden, solange es auf einer zukünftigen oder offenen Tagesordnung steht."
            )
    if errors:
        return [], errors
    return rows, []


def _preview(rows, topic_ids):
    topics = {row["topic_key"] for row in rows}
    existing_topics = {key for key in topics if topic_ids.get(key)}
    new_topics = topics - existing_topics
    agenda_rows = [row for row in rows if row.get("record_type") != "topic"]
    new_meetings = {
        (row["series_id"], row["meeting_date"]) for row in agenda_rows if row["existing_meeting_id"] is None
    }
    return {
        "rows": len(rows), "topics": len(topics), "meetings": len(new_meetings),
        "agenda_items": len(agenda_rows), "new_topics": len(new_topics),
        "existing_topics": len(existing_topics),
    }


def import_topic_agenda_csv(request, allowed_series_ids=None):
    if request.method == "POST" and request.POST.get("action") == "confirm":
        pending = request.session.get(SESSION_KEY)
        if not pending or pending.get("token") != request.POST.get("token"):
            messages.error(request, "Die Importvorschau ist abgelaufen. Bitte lade die CSV-Datei erneut hoch.")
            return redirect("management_topic_csv_import") if request.path.startswith("/verwaltung/") else redirect("admin:meetings_topic_csv_import")
        rows, errors = parse_topic_agenda_csv(pending["text"])
        if allowed_series_ids is not None:
            allowed = set(allowed_series_ids)
            for row in rows:
                if (
                    row["topic"].get("series_id") not in allowed
                    or (row.get("record_type") == "agenda" and row.get("series_id") not in allowed)
                    or (row.get("followup_series_id") and row.get("followup_series_id") not in allowed)
                ):
                    errors.append(
                        f"Zeile {row.get('row_number', '?')}: Die CSV enthält eine Besprechungsreihe, "
                        "für die keine Moderatorrechte bestehen."
                    )
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
                    if "status" in data and data["status"] is not None:
                        topic.status = data["status"]
                        topic.archive_previous_status = (
                            data.get("archive_previous_status", "open")
                            if data["status"] == "archived" else ""
                        )
                    if "assigned_to_id" in data:
                        topic.assigned_to_id = data["assigned_to_id"]
                    topic.save()
                    topic_records[key] = topic

                if row.get("record_type") == "topic":
                    continue
                meeting = Meeting.objects.filter(series_id=row["series_id"], date=row["meeting_date"]).first()
                if meeting is None:
                    meeting = Meeting.objects.create(
                        series_id=row["series_id"], date=row["meeting_date"], title=row["meeting_title"],
                    )
                    created_meetings += 1
                agenda_item = AgendaItem.objects.filter(meeting=meeting, topic=topic_records[key]).first()
                if agenda_item is None:
                    agenda_item = AgendaItem.objects.create(
                        meeting=meeting, topic=topic_records[key],
                        working_text=row["agenda_text"] if row["agenda_text_present"] else "",
                        assigned_to_id=row["agenda_assigned_to_id"] if row["agenda_assignment_present"] else None,
                        status=row["agenda_status"] if row["agenda_status_present"] else "open",
                        position=row["position"],
                        carried_forward=AgendaItem.objects.filter(
                            topic=topic_records[key], meeting__series_id=row["series_id"],
                            meeting__date__lt=row["meeting_date"],
                        ).exists(),
                    )
                    created_items += 1
                else:
                    changed_fields = []
                    if row["agenda_text_present"]:
                        agenda_item.working_text = row["agenda_text"]
                        changed_fields.append("working_text")
                    if row["agenda_assignment_present"]:
                        agenda_item.assigned_to_id = row["agenda_assigned_to_id"]
                        changed_fields.append("assigned_to")
                    if row["agenda_status_present"]:
                        agenda_item.status = row["agenda_status"]
                        changed_fields.append("status")
                    if changed_fields:
                        agenda_item.save(update_fields=changed_fields)
                    updated_items += 1

            # Restore the explicit source-to-follow-up relation after all rows
            # have been imported, so source rows may appear later in the CSV.
            for row in rows:
                if row.get("record_type") == "topic" or not row.get("followup_series_id"):
                    continue
                topic = topic_records[row["topic_key"]]
                source_meeting = Meeting.objects.filter(
                    series_id=row["followup_series_id"], date=row["followup_meeting_date"]
                ).first()
                target_meeting = Meeting.objects.get(series_id=row["series_id"], date=row["meeting_date"])
                source_item = AgendaItem.objects.filter(meeting=source_meeting, topic=topic).first() if source_meeting else None
                target_item = AgendaItem.objects.filter(meeting=target_meeting, topic=topic).first()
                if source_item is None or target_item is None or source_item.pk == target_item.pk:
                    raise ValueError("Eine Wiedervorlage verweist auf keinen passenden Quell-Tagesordnungspunkt.")
                if AgendaItem.objects.filter(followup_of=source_item).exclude(pk=target_item.pk).exists():
                    raise ValueError("Für den Quell-Tagesordnungspunkt existiert bereits eine andere Wiedervorlage.")
                target_item.followup_of = source_item
                target_item.save(update_fields=["followup_of"])
        request.session.pop(SESSION_KEY, None)
        messages.success(
            request,
            f"Import abgeschlossen: {created_topics} Themen neu angelegt, {updated_topics} aktualisiert, "
            f"{created_meetings} Termine angelegt, {created_items} Tagesordnungspunkte angelegt und "
            f"{updated_items} aktualisiert.",
        )
        return redirect("management_data") if request.path.startswith("/verwaltung/") else redirect("admin:meetings_topic_changelist")

    form = TopicAgendaCsvUploadForm(request.POST or None, request.FILES or None)
    preview = None
    errors = []
    if request.method == "POST" and form.is_valid():
        rows, errors = parse_topic_agenda_csv(form.csv_text)
        if allowed_series_ids is not None:
            allowed = set(allowed_series_ids)
            for row in rows:
                if (
                    row["topic"].get("series_id") not in allowed
                    or (row.get("record_type") == "agenda" and row.get("series_id") not in allowed)
                    or (row.get("followup_series_id") and row.get("followup_series_id") not in allowed)
                ):
                    errors.append(
                        f"Zeile {row.get('row_number', '?')}: Die CSV enthält eine Besprechungsreihe, "
                        "für die keine Moderatorrechte bestehen."
                    )
        if not errors:
            topic_ids = {}
            for row in rows:
                key = row["topic_key"]
                if key not in topic_ids:
                    matches = Topic.objects.filter(series_id=row["topic"]["series_id"], title__iexact=row["topic"]["title"])
                    topic_ids[key] = matches.first().pk if matches.exists() else None
            token = secrets.token_urlsafe(18)
            request.session[SESSION_KEY] = {"token": token, "text": form.csv_text, "topic_ids": topic_ids}
            preview = {**_preview(rows, topic_ids), "token": token}
    return render(request, "meetings/management_topic_csv_import.html" if request.path.startswith("/verwaltung/") else "admin/meetings/topic_csv_import.html", {
        **admin.site.each_context(request), "form": form, "preview": preview,
        "errors": errors, "title": "Themen und Tagesordnungspunkte importieren",
        "opts": Topic._meta,
    })
