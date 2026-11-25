import calendar
from pathlib import Path

from django import forms
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import content_disposition_header
from django.utils import formats, timezone

from .access import accessible_meetings, accessible_series, accessible_topics, auditor_readonly, is_admin, is_auditor, is_moderator, is_reader
from .audit import record_event
from .forms import UserDisplayModelChoiceField
from .models import AgendaItem, AuditEvent, Meeting, MeetingSeries, OrganizationSettings, SeriesAccess, Topic, TopicAttachment, TopicSnapshot
from .user_display import user_display_name


def topic_protocol_filename(topic):
    """Return the dated, filesystem-safe filename used by both PDF download methods."""
    title = "".join(
        "_" if not char.isprintable() or char in '\\\\/:*?"<>|' else char
        for char in topic.title
    ).strip(" .")
    return f"{timezone.localdate():%Y%m%d}-{title or 'Thema'}.pdf"


class TopicTitleForm(forms.ModelForm):
    assigned_to = UserDisplayModelChoiceField(
        queryset=get_user_model().objects.none(),
        required=False,
        label="Hauptzuständigkeit",
    )

    class Meta:
        model = Topic
        fields = ["title", "assigned_to"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["assigned_to"].queryset = get_user_model().objects.filter(
            is_active=True
        ).order_by("last_name", "first_name", "username")


class TopicStatusForm(forms.Form):
    status = forms.ChoiceField(
        label="Status",
        choices=[
            ("open", "Offen"),
            ("in_progress", "In Bearbeitung"),
            ("done", "Erledigt"),
        ],
    )


class NewTopicForm(forms.ModelForm):
    assigned_to = UserDisplayModelChoiceField(
        queryset=get_user_model().objects.none(), required=False,
        label="Hauptzuständigkeit",
    )

    class Meta:
        model = Topic
        fields = ["title", "series", "assigned_to"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["assigned_to"].queryset = get_user_model().objects.filter(
            is_active=True
        ).order_by("last_name", "first_name", "username")


TESTING_MODE_FILE = Path("/var/lib/meeting-manager-updater/testing-mode")


def _topic_testing_mode_enabled():
    return TESTING_MODE_FILE.is_file()


def _add_calendar_months(value, months):
    month_index = value.month - 1 + months
    year = value.year + month_index // 12
    month = month_index % 12 + 1
    day = min(value.day, calendar.monthrange(year, month)[1])
    return value.replace(year=year, month=month, day=day)


def _topic_archive_state(topic, today=None):
    if topic.status != "done":
        return False, "Das Thema kann erst archiviert werden, wenn sein Status auf „Erledigt“ steht."
    if _topic_testing_mode_enabled():
        return True, ""
    if not topic.completed_at:
        return False, "Das Abschlussdatum fehlt. Bitte das Thema einmal speichern, damit der Abschlusszeitpunkt erfasst wird."
    archive_date = _add_calendar_months(topic.completed_at, 6)
    today = today or timezone.localdate()
    if today < archive_date:
        return False, f"Eine Archivierung ist erst ab dem {formats.date_format(archive_date, 'DATE_FORMAT')} möglich (sechs Monate nach Abschluss)."
    return True, ""


def _update_completed_at(topic, old_status, new_status):
    if old_status != "done" and new_status == "done":
        topic.completed_at = timezone.localdate()
    elif old_status == "done" and new_status != "done":
        topic.completed_at = None


@login_required
@auditor_readonly
def topic_new(request):
    writable_series = accessible_series(request.user)
    writable_series = writable_series.exclude(user_access__role=SeriesAccess.ROLE_READER)
    if not writable_series.exists():
        return HttpResponseForbidden("Für diese Funktion ist eine Teilnehmer- oder Moderatorrolle erforderlich.")
    form = NewTopicForm(request.POST or None)
    form.fields["series"].queryset = writable_series.filter(active=True)
    form.fields["series"].required = True
    meetings = accessible_meetings(request.user).filter(
        series__in=writable_series.filter(active=True),
        date__gte=timezone.localdate(),
        finalized_at__isnull=True,
    ).select_related("series").order_by("series__name", "date")
    if request.method == "POST" and form.is_valid():
        meeting = meetings.filter(
            pk=request.POST.get("meeting"), series_id=form.cleaned_data["series"].pk
        ).first() if form.cleaned_data.get("series") else None
        if meeting is None:
            form.add_error(None, "Bitte wähle einen zukünftigen, noch nicht abgeschlossenen Termin der ausgewählten Besprechungsreihe.")
        else:
            with transaction.atomic():
                topic = form.save()
                position = (meeting.agenda_items.order_by("-position").values_list("position", flat=True).first()
                            if meeting.agenda_items.exists() else -1) + 1
                AgendaItem.objects.create(meeting=meeting, topic=topic, position=position)
                record_event(
                    actor=request.user, action="created",
                    summary=f"Thema „{topic.title}“ angelegt",
                    topic=topic, meeting=meeting,
                    changes={
                        "Titel": {"vorher": None, "nachher": topic.title},
                        "Hauptzuständigkeit": {
                            "vorher": None,
                            "nachher": user_display_name(topic.assigned_to) if topic.assigned_to else None,
                        },
                        "Erster Besprechungstermin": {"vorher": None, "nachher": meeting.date.isoformat()},
                    },
                )
            messages.success(request, f"„{topic.title}“ wurde auf die Tagesordnung am {formats.date_format(meeting.date, 'DATE_FORMAT')} gesetzt.")
            return redirect("topic_edit", pk=topic.pk)
    return render(request, "meetings/topic_form.html", {
        "form": form, "available_meetings": meetings,
        "is_reader": not writable_series.exists(),
    })


@login_required
@auditor_readonly
def topic_archive_toggle(request, pk):
    if request.method != "POST":
        return HttpResponseForbidden("Diese Aktion ist nur per POST möglich.")
    topic = get_object_or_404(accessible_topics(request.user), pk=pk)
    is_ajax = request.headers.get("x-requested-with") == "XMLHttpRequest"
    if topic.series_id is None or not is_moderator(request.user, topic.series):
        if is_ajax:
            return JsonResponse({"success": False, "error": "Keine Berechtigung zum Archivieren dieses Themas."}, status=403)
        return HttpResponseForbidden("Nur Moderator*innen der Besprechungsreihe dürfen Themen archivieren oder wieder öffnen.")
    archived_now = False
    with transaction.atomic():
        topic = Topic.objects.select_for_update().get(pk=topic.pk)
        if topic.status == "archived":
            previous_status = topic.archive_previous_status or "open"
            topic.status = previous_status if previous_status in {"open", "in_progress", "done"} else "open"
            topic.archive_previous_status = ""
            topic.save(update_fields=["status", "archive_previous_status", "updated_at"])
            record_event(
                actor=request.user, action="reopened",
                summary=f"Thema „{topic.title}“ aus dem Archiv wieder geöffnet",
                topic=topic,
                changes={"Themenstatus": {"vorher": "Archiviert", "nachher": dict(Topic.STATUS).get(topic.status, topic.status)}},
            )
            messages.success(request, f"„{topic.title}“ wurde wieder geöffnet.")
        else:
            can_archive, archive_reason = _topic_archive_state(topic)
            if not can_archive:
                if is_ajax:
                    return JsonResponse({"success": False, "error": archive_reason}, status=409)
                messages.error(request, archive_reason)
                return redirect("topic_edit", pk=topic.pk)
            has_future_agenda = topic.agenda_items.filter(
                meeting__finalized_at__isnull=True,
            ).exists()
            if has_future_agenda:
                error = "Das Thema kann noch nicht archiviert werden, solange es auf einer zukünftigen oder offenen Tagesordnung steht. Entferne zuerst die geplanten Tagesordnungspunkte."
                if is_ajax:
                    return JsonResponse({"success": False, "error": error}, status=409)
                messages.error(request, error)
                return redirect("topic_edit", pk=topic.pk)
            previous_status = topic.status
            attachments = list(TopicAttachment.objects.filter(topic=topic))
            stored_files = [
                (attachment.uploaded_file.storage, attachment.uploaded_file.name)
                for attachment in attachments if attachment.uploaded_file
            ]
            deleted_attachment_info = [
                {
                    "label": attachment.label,
                    "filename": Path(attachment.uploaded_file.name).name if attachment.uploaded_file else "",
                    "network_path": attachment.network_path,
                }
                for attachment in attachments
            ]
            TopicAttachment.objects.filter(topic=topic).delete()
            for storage, file_name in stored_files:
                transaction.on_commit(lambda storage=storage, file_name=file_name: storage.delete(file_name))
            topic.archive_previous_status = previous_status
            topic.status = "archived"
            topic.save(update_fields=["status", "archive_previous_status", "updated_at"])
            record_event(
                actor=request.user, action="archived",
                summary=f"Thema „{topic.title}“ archiviert",
                topic=topic,
                changes={
                    "Themenstatus": {"vorher": dict(Topic.STATUS).get(previous_status, previous_status), "nachher": "Archiviert"},
                    "Gelöschte Anlagen": deleted_attachment_info,
                },
            )
            messages.success(request, f"„{topic.title}“ wurde archiviert.")
            archived_now = True
    if is_ajax:
        action_message = f"„{topic.title}“ wurde " + ("archiviert." if archived_now else "wieder geöffnet.")
        return JsonResponse({"success": True, "archived": archived_now, "message": action_message})
    return redirect("topic_edit", pk=topic.pk)


@login_required
@auditor_readonly
@transaction.atomic
def topic_detail(request, pk):
    topic = get_object_or_404(accessible_topics(request.user), pk=pk)
    reader = is_reader(request.user, topic.series) or (topic.series_id is None)
    # ModelForm validation writes submitted values onto its instance before
    # is_valid() returns. Snapshot persisted values before constructing it.
    original_values = Topic.objects.filter(pk=topic.pk).values(
        "title", "assigned_to_id", "status"
    ).get()
    form = TopicTitleForm(request.POST or None, instance=topic)
    updating_details = request.method == "POST" and "save_topic_details" in request.POST
    status_form = TopicStatusForm(
        request.POST if request.method == "POST" and ("save_topic_details" in request.POST or "update_topic_status" in request.POST) and topic.status != "archived" else None,
        initial={"status": topic.status if topic.status in {"open", "in_progress", "done"} else "open"},
    )
    if reader:
        form.fields["title"].disabled = True
        form.fields["assigned_to"].disabled = True
    if request.method == "POST":
        if reader:
            return HttpResponseForbidden("Leser*innen haben ausschließlich Leserechte.")
        if updating_details:
            details_valid = form.is_valid()
            status_valid = topic.status == "archived" or status_form.is_valid()
            if details_valid and status_valid:
                old_title = original_values["title"]
                old_assignee_id = original_values["assigned_to_id"]
                old_assignee = (
                    get_user_model().objects.filter(pk=old_assignee_id).first()
                    if old_assignee_id else None
                )
                changed_fields = set(form.changed_data)
                changes = {}
                with transaction.atomic():
                    updated = form.save(commit=False)
                    if "title" in changed_fields:
                        changes["Titel"] = {"vorher": old_title, "nachher": updated.title}
                    if "assigned_to" in changed_fields:
                        changes["Zuständigkeit"] = {
                            "vorher": user_display_name(old_assignee) if old_assignee else None,
                            "nachher": user_display_name(updated.assigned_to) if updated.assigned_to else None,
                        }
                    if topic.status != "archived":
                        new_status = status_form.cleaned_data["status"]
                        if new_status != original_values["status"]:
                            changes["Themenstatus"] = {
                                "vorher": dict(Topic.STATUS).get(original_values["status"], original_values["status"]),
                                "nachher": dict(Topic.STATUS).get(new_status, new_status),
                            }
                            updated.status = new_status
                            _update_completed_at(updated, original_values["status"], new_status)
                    if updated.status == "done" and not updated.completed_at:
                        updated.completed_at = timezone.localdate()
                        changes["Abschlussdatum"] = {"vorher": None, "nachher": updated.completed_at.isoformat()}
                    if changes:
                        updated.save()
                        if "assigned_to" in changed_fields:
                            form.save_m2m()
                        record_event(
                            actor=request.user, action="updated",
                            summary=f"Thema „{updated.title}“ geändert",
                            topic=updated, changes=changes,
                        )
                        messages.success(request, "Thema gespeichert.")
                    else:
                        messages.info(request, "Es wurden keine Änderungen vorgenommen.")
                return redirect("topic_edit", pk=topic.pk)
        elif "update_topic_status" in request.POST:
            # Backwards-compatible handling for clients still submitting the
            # earlier status-only form.
            if topic.status == "archived":
                return HttpResponseForbidden("Archivierte Themen müssen zuerst wieder geöffnet werden.")
            if status_form.is_valid():
                new_status = status_form.cleaned_data["status"]
                old_status = original_values["status"]
                if new_status != old_status:
                    with transaction.atomic():
                        topic.status = new_status
                        _update_completed_at(topic, old_status, new_status)
                        topic.save(update_fields=["status", "completed_at", "updated_at"])
                        record_event(
                            actor=request.user, action="updated",
                            summary=f"Status des Themas „{topic.title}“ geändert",
                            topic=topic,
                            changes={"Themenstatus": {
                                "vorher": dict(Topic.STATUS).get(old_status, old_status),
                                "nachher": dict(Topic.STATUS).get(new_status, new_status),
                            }},
                        )
                    messages.success(request, "Themenstatus gespeichert.")
                else:
                    messages.info(request, "Der Themenstatus ist unverändert.")
                return redirect("topic_edit", pk=topic.pk)
        elif form.is_valid():
            # Capture persisted values before ModelForm.save() mutates its instance.
            old_title = original_values["title"]
            old_assignee_id = original_values["assigned_to_id"]
            old_assignee = (
                get_user_model().objects.filter(pk=old_assignee_id).first()
                if old_assignee_id else None
            )
            changed_fields = set(form.changed_data)
            with transaction.atomic():
                updated = form.save()
                changes = {}
                if "title" in changed_fields:
                    changes["Titel"] = {"vorher": old_title, "nachher": updated.title}
                if "assigned_to" in changed_fields:
                    changes["Hauptzuständigkeit"] = {
                        "vorher": user_display_name(old_assignee) if old_assignee else None,
                        "nachher": user_display_name(updated.assigned_to) if updated.assigned_to else None,
                    }
                if changes:
                    record_event(
                        actor=request.user, action="updated",
                        summary=f"Thema „{updated.title}“ geändert",
                        topic=updated, changes=changes,
                    )
                    messages.success(request, "Thema gespeichert.")
                else:
                    messages.info(request, "Es wurden keine Änderungen vorgenommen.")
            return redirect("topic_edit", pk=topic.pk)

    visible_meetings = accessible_meetings(request.user)
    items = list(
        AgendaItem.objects.filter(topic=topic, meeting__in=visible_meetings)
        .select_related("meeting", "meeting__series", "assigned_to")
        .order_by("-meeting__date", "position", "pk")
    )
    snapshots = {
        snapshot.meeting_id: snapshot
        for snapshot in TopicSnapshot.objects.filter(
            topic_id=topic.pk, meeting__in=visible_meetings
        ).select_related("meeting", "meeting__series")
    }
    items_by_meeting = {item.meeting_id: item for item in items}
    meetings_by_id = {item.meeting_id: item.meeting for item in items}
    meetings_by_id.update({snapshot.meeting_id: snapshot.meeting for snapshot in snapshots.values()})
    topic_meetings = sorted(meetings_by_id.values(), key=lambda meeting: (meeting.date, meeting.pk))
    for item in items:
        snapshot = snapshots.get(item.meeting_id)
        item.display_text = snapshot.text if snapshot else item.working_text
        item.snapshot_exists = snapshot is not None

    writable_series = accessible_series(request.user).exclude(user_access__role=SeriesAccess.ROLE_READER)
    return render(request, "meetings/topic_form.html", {
        "form": form,
        "status_form": status_form,
        "topic": topic,
        "topic_protocol_filename": topic_protocol_filename(topic),
        "can_archive_topic": topic.series_id is not None and is_moderator(request.user, topic.series),
        "topic_archive_allowed": _topic_archive_state(topic)[0],
        "topic_archive_reason": _topic_archive_state(topic)[1],
        "archived_attachment_info": [
            attachment_info
            for archive_event in AuditEvent.objects.filter(topic=topic, action="archived").order_by("created_at", "pk")
            for attachment_info in (archive_event.changes or {}).get("Gelöschte Anlagen", [])
        ],
        "is_reader": reader,
        "topic_agenda_items": items,
        "transfer_series": writable_series.filter(active=True).exclude(pk=topic.series_id),
        "assignees": get_user_model().objects.filter(is_active=True).order_by("last_name", "first_name", "username"),
    })


@login_required
@auditor_readonly
@transaction.atomic
def edit_topic_agenda_item(request, pk, item_pk):
    if request.method != "POST":
        return HttpResponseForbidden()
    item = get_object_or_404(
        AgendaItem.objects.select_related("topic", "meeting__series"),
        pk=item_pk, topic_id=pk, meeting__in=accessible_meetings(request.user),
    )
    if (
        is_reader(request.user, item.meeting.series)
        or (item.meeting.series_id is None)
        or item.meeting.finalized_at
    ):
        return HttpResponseForbidden("Dieser Tagesordnungspunkt ist schreibgeschützt.")
    User = get_user_model()
    assignee_id = request.POST.get("assigned_to") or None
    assignee = None
    if assignee_id:
        assignee = User.objects.filter(pk=assignee_id, is_active=True).first()
        if assignee is None:
            messages.error(request, "Bitte wähle eine gültige verantwortliche Person.")
            return redirect("topic_edit", pk=pk)
    old_text = item.working_text
    old_assignee = item.assigned_to_id
    old_assignee_user = User.objects.filter(pk=old_assignee).first() if old_assignee else None
    changes = {}
    update_fields = []
    if "working_text" in request.POST:
        new_text = request.POST.get("working_text", "")
        if old_text != new_text:
            item.working_text = new_text
            update_fields.append("working_text")
            changes["Besprechungstext"] = {"vorher": old_text, "nachher": new_text}
    if "assigned_to" in request.POST and old_assignee != (assignee.pk if assignee else None):
        item.assigned_to = assignee
        update_fields.append("assigned_to")
        changes["Zuständigkeit"] = {
            "vorher": user_display_name(old_assignee_user) if old_assignee_user else None,
            "nachher": user_display_name(assignee) if assignee else None,
        }
    if update_fields:
        item.save(update_fields=update_fields)
        record_event(
            actor=request.user, action="agenda_edited",
            summary=f"Agenda-Punkt „{item.topic.title}“ am {formats.date_format(item.meeting.date, 'DATE_FORMAT')} geändert",
            topic=item.topic, meeting=item.meeting, changes=changes,
        )
        messages.success(request, "Tagesordnungstext gespeichert.")
    else:
        messages.info(request, "Es wurden keine Änderungen vorgenommen.")
    return redirect("topic_edit", pk=pk)


@login_required
def topic_protocol_pdf(request, pk):
    """Download a topic-centred protocol containing its visible agenda history."""
    topic = get_object_or_404(
        accessible_topics(request.user).select_related("series", "assigned_to"), pk=pk
    )
    visible_meetings = accessible_meetings(request.user)
    items = list(
        AgendaItem.objects.filter(topic=topic, meeting__in=visible_meetings)
        .select_related("meeting", "meeting__series", "assigned_to")
        .order_by("meeting__date", "meeting_id", "position", "pk")
    )
    snapshots = {
        snapshot.meeting_id: snapshot
        for snapshot in TopicSnapshot.objects.filter(
            topic_id=topic.pk, meeting__in=visible_meetings
        ).select_related("meeting", "meeting__series")
    }
    items_by_meeting = {item.meeting_id: item for item in items}
    meetings_by_id = {item.meeting_id: item.meeting for item in items}
    meetings_by_id.update({
        snapshot.meeting_id: snapshot.meeting
        for snapshot in snapshots.values()
    })
    topic_meetings = sorted(
        meetings_by_id.values(), key=lambda meeting: (meeting.date, meeting.pk)
    )

    from io import BytesIO
    from xml.sax.saxutils import escape
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.lib.utils import ImageReader
    from reportlab.platypus import SimpleDocTemplate, Paragraph, HRFlowable, KeepTogether

    organization = OrganizationSettings.objects.filter(pk=1).first()
    organization_name = organization.name.strip() if organization and organization.name else ""
    brand = OrganizationSettings.current_brand_colors()
    try:
        primary = colors.HexColor(brand.get("primary_color") or "#00549F")
    except (TypeError, ValueError):
        primary = colors.HexColor("#00549F")
    try:
        secondary = colors.HexColor(brand.get("secondary_color") or "#8FC5FF")
    except (TypeError, ValueError):
        secondary = colors.HexColor("#8FC5FF")

    logo_image = None
    if organization and organization.logo and organization.logo.name:
        logo_field = organization.logo
        prepared_logo = organization.logo_png if logo_field.name.lower().endswith(".svg") else logo_field
        if prepared_logo:
            try:
                prepared_logo.open("rb")
                try:
                    logo_data = prepared_logo.read()
                finally:
                    prepared_logo.close()
                if logo_data:
                    logo_image = ImageReader(BytesIO(logo_data))
            except Exception:
                return HttpResponse(
                    "Das konfigurierte Organisationslogo konnte nicht geladen werden. Bitte prüfen Sie die Logo-Datei.",
                    status=503, content_type="text/plain; charset=utf-8",
                )
        else:
            return HttpResponse(
                "Für das konfigurierte SVG-Logo liegt keine vorbereitete PNG-Version vor.",
                status=503, content_type="text/plain; charset=utf-8",
            )

    buffer = BytesIO()
    left_margin = right_margin = 20 * mm
    document = SimpleDocTemplate(
        buffer, pagesize=A4, leftMargin=left_margin, rightMargin=right_margin,
        topMargin=36 * mm, bottomMargin=25 * mm,
        title=f"Themenprotokoll – {topic.title}",
        author=f"Meeting Manager – {organization_name}" if organization_name else "Meeting Manager",
        subject=f"Besprechungsverlauf zum Thema {topic.title}",
    )
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="TopicProtocolSection", parent=styles["Heading2"], fontName="Helvetica-Bold",
        fontSize=13, leading=17, textColor=primary, spaceBefore=5 * mm, spaceAfter=2 * mm,
        keepWithNext=True,
    ))
    styles.add(ParagraphStyle(
        name="TopicProtocolBody", parent=styles["BodyText"], fontName="Helvetica",
        fontSize=9.5, leading=15, textColor=colors.HexColor("#263445"), spaceAfter=2 * mm,
        splitLongWords=True,
    ))
    styles.add(ParagraphStyle(
        name="TopicProtocolMeta", parent=styles["Normal"], fontName="Helvetica",
        fontSize=8.5, leading=12, textColor=colors.HexColor("#526170"),
    ))
    created_label = formats.date_format(timezone.localtime(timezone.now()), "DATETIME_FORMAT")
    responsible = (
        user_display_name(topic.assigned_to, include_short_description=True)
        if topic.assigned_to else "Nicht festgelegt"
    )
    story = [
        Paragraph("Themeninformationen", styles["TopicProtocolSection"]),
        Paragraph(f"<b>Hauptzuständigkeit:</b> {escape(responsible)}", styles["TopicProtocolBody"]),
        Paragraph(f"<b>Besprechungsreihe:</b> {escape(str(topic.series) if topic.series else '—')}", styles["TopicProtocolBody"]),
        Paragraph(f"<b>Status:</b> {escape(topic.get_status_display())}", styles["TopicProtocolBody"]),
        Paragraph(f"<b>Erstellt:</b> {formats.date_format(topic.created_at, 'DATE_FORMAT')} &nbsp;&nbsp; <b>Zuletzt geändert:</b> {formats.date_format(topic.updated_at, 'DATE_FORMAT')}", styles["TopicProtocolBody"]),
        HRFlowable(width="100%", thickness=0.8, color=secondary, spaceBefore=1 * mm, spaceAfter=2 * mm),
        Paragraph("Besprechungsverlauf", styles["TopicProtocolSection"]),
    ]
    for meeting in topic_meetings:
        item = items_by_meeting.get(meeting.pk)
        snapshot = snapshots.get(meeting.pk)
        text = snapshot.text if snapshot else (item.working_text if item else "")
        status = dict(AgendaItem.STATUS).get(snapshot.status, snapshot.status) if snapshot else (
            item.get_status_display() if item else "Unbekannt"
        )
        responsible_name = snapshot.responsible_name if snapshot else (
            user_display_name(item.assigned_to, include_short_description=True)
            if item and item.assigned_to else responsible
        )
        series_name = meeting.series.name if meeting.series_id else (
            meeting.archived_series_name or "Gelöschte Besprechungsreihe"
        )
        meeting_label = f"{series_name} · {formats.date_format(meeting.date, 'DATE_FORMAT')}"
        parts = [
            Paragraph(escape(meeting_label), styles["TopicProtocolSection"]),
            Paragraph(f"<b>Status:</b> {escape(status)} &nbsp;&nbsp; <b>Verantwortlich:</b> {escape(responsible_name or 'Nicht festgelegt')}", styles["TopicProtocolMeta"]),
            Paragraph(escape(text or "Kein Text hinterlegt.").replace("\n", "<br/>"), styles["TopicProtocolBody"]),
        ]
        story.append(KeepTogether(parts))
    if not topic_meetings:
        story.append(Paragraph("Für dieses Thema liegen noch keine Besprechungstexte vor.", styles["TopicProtocolBody"]))

    from reportlab.pdfgen import canvas as pdf_canvas
    class NumberedCanvas(pdf_canvas.Canvas):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._saved_page_states = []
        def showPage(self):
            self._saved_page_states.append(dict(self.__dict__))
            self._startPage()
        def save(self):
            page_count = len(self._saved_page_states)
            for state in self._saved_page_states:
                self.__dict__.update(state)
                self.saveState()
                page_top = A4[1] - 11 * mm
                right_edge = A4[0] - right_margin
                if logo_image:
                    width, height = logo_image.getSize()
                    scale = min((18 * mm) / height, (42 * mm) / width)
                    self.drawImage(logo_image, right_edge - width * scale, page_top - height * scale,
                                   width=width * scale, height=height * scale, mask="auto")
                self.setFillColor(colors.HexColor("#263445"))
                self.setFont("Helvetica-Bold", 8.5)
                if organization_name:
                    self.drawString(left_margin, page_top - 2 * mm, organization_name[:75])
                self.setFillColor(primary)
                self.setFont("Helvetica-Bold", 13)
                self.drawCentredString(A4[0] / 2, page_top - 3 * mm, "THEMENPROTOKOLL")
                self.setFillColor(colors.HexColor("#526170"))
                self.setFont("Helvetica", 9)
                self.drawCentredString(A4[0] / 2, page_top - 10 * mm, topic.title[:90])
                self.setStrokeColor(primary)
                self.setLineWidth(1.1)
                self.line(left_margin, A4[1] - 32 * mm, right_edge, A4[1] - 32 * mm)
                footer_y = 15 * mm
                self.setStrokeColor(colors.HexColor("#DCE3EA"))
                self.setLineWidth(0.5)
                self.line(left_margin, footer_y + 4 * mm, right_edge, footer_y + 4 * mm)
                self.setFillColor(colors.HexColor("#687684"))
                self.setFont("Helvetica", 7)
                self.drawString(left_margin, footer_y, "Themenprotokoll · aktueller sichtbarer Datenstand")
                self.drawString(left_margin, footer_y - 4 * mm, f"PDF erstellt: {created_label}"[:105])
                self.setFillColor(colors.HexColor("#263445"))
                self.setFont("Helvetica-Bold", 7.5)
                self.drawRightString(right_edge, footer_y - 1 * mm, f"Seite {self._pageNumber} von {page_count}")
                self.restoreState()
                super().showPage()
            super().save()

    document.build(story, canvasmaker=NumberedCanvas)
    pdf_content = buffer.getvalue()
    response = HttpResponse(pdf_content, content_type="application/pdf")
    response["Content-Disposition"] = content_disposition_header(
        True, topic_protocol_filename(topic)
    )
    return response
