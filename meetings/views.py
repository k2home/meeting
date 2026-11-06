from io import BytesIO
from pathlib import Path
from xml.sax.saxutils import escape

from django.contrib import messages
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.db.models import F, Q, Window
from django.db.models.functions import RowNumber
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.text import slugify
from django.utils.http import url_has_allowed_host_and_scheme
from .forms import UsernameLoginForm, TopicForm, TopicCommentForm, AgendaTextForm, AttachmentForm, SeriesForm, MeetingParticipantsForm
from .models import Meeting, MeetingSeries, Topic, TopicAttachment, TopicTransferHistory, AuditEvent, AgendaItem
from .audit import record_event
from .services import ensure_agenda, generate_meetings, finalize_meeting

def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    form = UsernameLoginForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        next_url = request.POST.get("next") or request.GET.get("next", "")
        if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
            return redirect(next_url)
        return redirect("dashboard")
    return render(request, "meetings/login.html", {"form": form, "next": request.GET.get("next", "")})

@login_required
def logout_view(request):
    if request.method != "POST":
        return HttpResponseForbidden("Bitte über die Abmelden-Schaltfläche abmelden.")
    logout(request)
    return redirect("login")

UserModel = get_user_model()


def admin_only(user):
    return user.is_authenticated and user.is_staff

@login_required
def dashboard(request):
    today = timezone.localdate()
    meetings = (
        Meeting.objects.filter(date__gte=today)
        .annotate(series_position=Window(
            expression=RowNumber(),
            partition_by=[F("series_id")],
            order_by=[F("date").asc(), F("pk").asc()],
        ))
        .filter(series_position__lte=2)
        .select_related("series")
        .order_by("date", "series__name", "pk")
    )
    topics = Topic.objects.select_related("series", "assigned_to")
    query = request.GET.get("q", "").strip()
    selected_status = request.GET.get("status", "open")
    selected_series = request.GET.get("series", "")
    selected_assignee = request.GET.get("assigned_to", "")
    selected_due = request.GET.get("due", "")

    if selected_status in {"open", "done", "archived"}:
        topics = topics.filter(status=selected_status)
    elif selected_status != "all":
        selected_status = "open"

    if query:
        topics = topics.filter(
            Q(title__icontains=query)
            | Q(description__icontains=query)
            | Q(series__name__icontains=query)
            | Q(assigned_to__username__icontains=query)
            | Q(assigned_to__first_name__icontains=query)
            | Q(assigned_to__last_name__icontains=query)
        )
    if selected_series.isdigit():
        topics = topics.filter(series_id=int(selected_series))
    else:
        selected_series = ""
    if selected_assignee == "unassigned":
        topics = topics.filter(assigned_to__isnull=True)
    elif selected_assignee.isdigit():
        topics = topics.filter(assigned_to_id=int(selected_assignee))
    else:
        selected_assignee = ""
    if selected_due == "overdue":
        topics = topics.filter(due_date__lt=today, status="open")
    elif selected_due == "today":
        topics = topics.filter(due_date=today)
    elif selected_due == "without_date":
        topics = topics.filter(due_date__isnull=True)
    elif selected_due == "future":
        topics = topics.filter(due_date__gt=today)

    overdue_count = Topic.objects.filter(status="open", due_date__lt=today).count()
    return render(request, "meetings/dashboard.html", {
        "meetings": meetings, "topics": topics, "overdue_count": overdue_count, "today": today,
        "query": query, "selected_status": selected_status, "selected_series": selected_series,
        "selected_assignee": selected_assignee, "selected_due": selected_due,
        "series_options": MeetingSeries.objects.order_by("name"),
        "assignee_options": UserModel.objects.filter(is_active=True).order_by("username"),
        "result_count": topics.count(),
    })

@login_required
def my_tasks(request):
    """Show the signed-in user's open topics, with overdue work first."""
    today = timezone.localdate()
    topics = (
        Topic.objects.filter(assigned_to=request.user, status="open")
        .select_related("series")
        .order_by(F("due_date").asc(nulls_last=True), "title")
    )
    return render(request, "meetings/my_tasks.html", {
        "topics": topics,
        "today": today,
        "overdue_count": topics.filter(due_date__lt=today).count(),
        "due_today_count": topics.filter(due_date=today).count(),
        "without_due_date_count": topics.filter(due_date__isnull=True).count(),
    })


@login_required
def agenda_reorder(request, pk):
    if request.method != "POST":
        return HttpResponseForbidden()
    meeting = get_object_or_404(Meeting, pk=pk)
    if meeting.finalized_at:
        messages.error(request, "Die Tagesordnung einer abgeschlossenen Besprechung kann nicht mehr geändert werden.")
        return redirect("meeting", pk=pk)
    current_ids = list(meeting.agenda_items.order_by("position", "id").values_list("id", flat=True))
    submitted_ids = request.POST.getlist("item_ids")
    try:
        ordered_ids = [int(value) for value in submitted_ids]
    except (TypeError, ValueError):
        ordered_ids = []
    if len(ordered_ids) != len(current_ids) or set(ordered_ids) != set(current_ids):
        messages.error(request, "Die Reihenfolge konnte nicht gespeichert werden. Bitte Seite neu laden.")
        return redirect("meeting", pk=pk)
    items_by_id = {item.pk: item for item in AgendaItem.objects.filter(meeting=meeting, pk__in=ordered_ids)}
    ordered_items = []
    for position, item_id in enumerate(ordered_ids):
        item = items_by_id[item_id]
        item.position = position
        ordered_items.append(item)
    with transaction.atomic():
        AgendaItem.objects.bulk_update(ordered_items, ["position"])
    messages.success(request, "Reihenfolge der Tagesordnung gespeichert.")
    return redirect("meeting", pk=pk)


@login_required
def meeting_detail(request, pk):
    meeting = get_object_or_404(Meeting.objects.select_related("series"), pk=pk)
    items = ensure_agenda(meeting)
    if request.method == "POST":
        if meeting.finalized_at:
            messages.error(request, "Eine abgeschlossene Besprechung kann nicht mehr geändert werden.")
            return redirect("meeting", pk=pk)
        if request.POST.get("save_participants"):
            before = [u.get_full_name().strip() or u.username for u in meeting.participants.all()]
            participant_form = MeetingParticipantsForm(request.POST, instance=meeting)
            if participant_form.is_valid():
                participant_form.save()
                after = [u.get_full_name().strip() or u.username for u in meeting.participants.all()]
                if before != after:
                    record_event(
                        actor=request.user, action="updated",
                        summary=f"Teilnehmerliste für „{meeting.series.name}“ am {meeting.date:%d.%m.%Y} geändert",
                        meeting=meeting,
                        changes={"Teilnehmer": {"vorher": before, "nachher": after}},
                    )
                messages.success(request, "Teilnehmerliste gespeichert.")
            else:
                messages.error(request, "Bitte prüfe die Teilnehmerauswahl.")
                return render(request, "meetings/meeting.html", {
                    "meeting": meeting, "items": items, "participant_form": participant_form,
                })
        else:
            item_id = request.POST.get("item_id")
            if item_id:
                item = get_object_or_404(AgendaItem, pk=item_id, meeting=meeting)
                form = AgendaTextForm(request.POST, instance=item)
                if form.is_valid():
                    old_text = item.working_text
                    saved = form.save()
                    if old_text != saved.working_text:
                        record_event(actor=request.user, action="agenda_edited",
                            summary=f"Agendatext für „{item.topic.title}“ in {meeting.date:%d.%m.%Y} geändert",
                            topic=item.topic, meeting=meeting,
                            changes={"Text": {"vorher": old_text, "nachher": saved.working_text}})
                    messages.success(request, "Agendatext gespeichert.")
        return redirect("meeting", pk=pk)
    participant_form = MeetingParticipantsForm(instance=meeting)
    return render(request, "meetings/meeting.html", {
        "meeting": meeting, "items": items, "participant_form": participant_form,
    })

@login_required
def topic_edit(request, pk):
    topic = get_object_or_404(Topic, pk=pk)
    original_topic = Topic.objects.select_related("series", "assigned_to").get(pk=pk)
    form = TopicForm(request.POST or None, instance=topic)
    if request.method == "POST" and form.is_valid():
        old_series = original_topic.series
        before = {"title": original_topic.title, "description": original_topic.description,
                  "due_date": original_topic.due_date.isoformat() if original_topic.due_date else None,
                  "status": original_topic.status,
                  "series": str(original_topic.series) if original_topic.series else None,
                  "assigned_to": str(original_topic.assigned_to) if original_topic.assigned_to else None}
        updated_topic = form.save(commit=False)
        new_series = updated_topic.series
        after = {"title": updated_topic.title, "description": updated_topic.description,
                 "due_date": updated_topic.due_date.isoformat() if updated_topic.due_date else None,
                 "status": updated_topic.status, "series": str(new_series) if new_series else None,
                 "assigned_to": str(updated_topic.assigned_to) if updated_topic.assigned_to else None}
        labels = {"title": "Titel", "description": "Beschreibung",
                  "due_date": "Fälligkeitsdatum", "status": "Status", "series": "Besprechungsreihe",
                  "assigned_to": "Verantwortlich"}
        changes = {
            labels[field]: {"vorher": before[field], "nachher": after[field]}
            for field in form.changed_data if field in labels
        }
        with transaction.atomic():
            if old_series != new_series:
                TopicTransferHistory.objects.create(topic=topic, from_series=old_series, to_series=new_series,
                    transferred_by=request.user, note="Zuordnung im Themenformular geändert")
            updated_topic.save()
            if changes:
                summary = (f"Zuständigkeit für „{updated_topic.title}“ geändert"
                           if "assigned_to" in form.changed_data and len(form.changed_data) == 1
                           else f"Thema „{updated_topic.title}“ geändert")
                record_event(actor=request.user, action="updated",
                    summary=summary, topic=updated_topic, changes=changes)
        messages.success(request, "Thema gespeichert.")
        return redirect("topic_edit", pk=topic.pk)
    return render(request, "meetings/topic_form.html", {
        "form": form, "topic": topic,
        "transfer_series": MeetingSeries.objects.filter(active=True).exclude(pk=topic.series_id),
    })

@login_required
def topic_new(request):
    form = TopicForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        topic = form.save()
        record_event(actor=request.user, action="created", summary=f"Thema „{topic.title}“ angelegt",
                     topic=topic, changes={"Titel": {"vorher": None, "nachher": topic.title}})
        messages.success(request, "Thema angelegt.")
        return redirect("topic_edit", pk=topic.pk)
    return render(request, "meetings/topic_form.html", {"form": form})

@login_required
def topic_archive(request, pk):
    if request.method != "POST":
        return HttpResponseForbidden()
    topic = get_object_or_404(Topic, pk=pk)
    if topic.status == "archived":
        messages.info(request, "Dieses Thema ist bereits archiviert.")
    else:
        topic.status = "archived"
        topic.save(update_fields=["status", "updated_at"])
        record_event(actor=request.user, action="archived", summary=f"Thema „{topic.title}“ archiviert",
                     topic=topic, changes={"Status": {"vorher": "Offen", "nachher": "Archiviert"}})
        messages.success(request, "Thema wurde archiviert.")
    return redirect("archive")

@login_required
def topic_reopen(request, pk):
    if request.method != "POST":
        return HttpResponseForbidden()
    topic = get_object_or_404(Topic, pk=pk, status="archived")
    topic.status = "open"
    topic.save(update_fields=["status", "updated_at"])
    record_event(actor=request.user, action="reopened", summary=f"Thema „{topic.title}“ wieder geöffnet",
                 topic=topic, changes={"Status": {"vorher": "Archiviert", "nachher": "Offen"}})
    messages.success(request, "Thema wurde wieder geöffnet.")
    return redirect("topic_edit", pk=topic.pk)

@login_required
def topic_transfer(request, pk):
    if request.method != "POST":
        return HttpResponseForbidden()
    topic = get_object_or_404(Topic, pk=pk)
    target = get_object_or_404(MeetingSeries, pk=request.POST.get("series"), active=True)
    if topic.series_id == target.pk:
        messages.info(request, "Das Thema ist bereits dieser Besprechungsreihe zugeordnet.")
        return redirect("topic_edit", pk=topic.pk)
    note = request.POST.get("note", "").strip()[:500]
    with transaction.atomic():
        TopicTransferHistory.objects.create(
            topic=topic, from_series=topic.series, to_series=target,
            transferred_by=request.user, note=note,
        )
        old_series_name = str(topic.series) if topic.series else "Ohne Reihe"
        topic.series = target
        topic.save(update_fields=["series", "updated_at"])
        record_event(actor=request.user, action="transferred",
                     summary=f"Thema „{topic.title}“ nach „{target.name}“ übertragen", topic=topic,
                     changes={"Besprechungsreihe": {"vorher": old_series_name, "nachher": target.name},
                              "Notiz": note})
    messages.success(request, f"Thema wurde nach „{target.name}“ übertragen. Die bisherige Zuordnung bleibt in der Historie erhalten.")
    return redirect("topic_edit", pk=topic.pk)

@login_required
def archive(request):
    topics = Topic.objects.filter(status="archived").select_related("series")
    return render(request, "meetings/archive.html", {"topics": topics})

@login_required
def attachment_add(request, pk):
    topic = get_object_or_404(Topic, pk=pk)
    form = AttachmentForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.topic = topic
        obj.save()
        record_event(actor=request.user, action="attachment_added",
                     summary=f"Anlage „{obj.label}“ zu „{topic.title}“ hinzugefügt", topic=topic,
                     changes={"Bezeichnung": obj.label, "Datei": obj.uploaded_file.name if obj.uploaded_file else None,
                              "Netzwerkpfad": obj.network_path or None})
        messages.success(request, "Anlage hinzugefügt.")
        return redirect("topic_edit", pk=pk)
    return render(request, "meetings/attachment_form.html", {"form": form, "topic": topic})

def _protocol_entries(meeting):
    """Return the immutable snapshot for finalized meetings or the live draft."""
    if meeting.finalized_at:
        return [
            {
                "title": snapshot.topic_title,
                "text": snapshot.text,
                "status": dict(Topic.STATUS).get(snapshot.status, snapshot.status),
            }
            for snapshot in meeting.snapshots.all()
        ]
    return [
        {
            "title": item.topic.title,
            "text": item.working_text,
            "status": item.topic.get_status_display(),
        }
        for item in ensure_agenda(meeting)
    ]


def _meeting_participant_names(meeting):
    return [
        user.get_full_name().strip() or user.username
        for user in meeting.participants.filter(is_active=True).order_by("last_name", "first_name", "username")
    ]


def _protocol_filename(meeting, extension):
    series = slugify(meeting.series.name) or "besprechung"
    return f"protokoll-{series}-{meeting.date:%Y-%m-%d}.{extension}"


@login_required
def protocol_pdf(request, pk):
    meeting = get_object_or_404(Meeting.objects.select_related("series"), pk=pk)
    entries = _protocol_entries(meeting)

    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, KeepTogether

    buffer = BytesIO()
    document = SimpleDocTemplate(
        buffer, pagesize=A4, rightMargin=20 * mm, leftMargin=20 * mm,
        topMargin=20 * mm, bottomMargin=18 * mm,
        title=f"Protokoll – {meeting.series.name}",
        author="Meeting Manager",
    )
    styles = getSampleStyleSheet()
    regular_font = "Helvetica"
    bold_font = "Helvetica-Bold"
    font_path = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
    bold_path = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
    if font_path.exists() and bold_path.exists():
        if "MeetingDejaVu" not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont("MeetingDejaVu", str(font_path)))
            pdfmetrics.registerFont(TTFont("MeetingDejaVu-Bold", str(bold_path)))
        regular_font, bold_font = "MeetingDejaVu", "MeetingDejaVu-Bold"

    styles.add(ParagraphStyle(
        name="ProtocolTitle", parent=styles["Title"], fontName=bold_font,
        alignment=TA_CENTER, fontSize=19, leading=24, spaceAfter=8 * mm,
    ))
    styles.add(ParagraphStyle(
        name="ProtocolTopic", parent=styles["Heading2"], fontName=bold_font,
        fontSize=12, leading=16, spaceBefore=5 * mm, spaceAfter=2 * mm,
        keepWithNext=True,
    ))
    styles["Normal"].fontName = regular_font
    styles["Normal"].leading = 14

    story = [
        Paragraph("Protokoll", styles["ProtocolTitle"]),
        Paragraph(escape(meeting.series.name), styles["Heading2"]),
        Paragraph(f"Datum: {meeting.date:%d.%m.%Y}", styles["Normal"]),
        Paragraph(
            "Gesicherter Stand" if meeting.finalized_at else "Entwurf – nicht abgeschlossen",
            styles["Normal"],
        ),
    ]
    participant_names = _meeting_participant_names(meeting)
    story.append(Paragraph("Teilnehmer", styles["Heading2"]))
    if participant_names:
        for name in participant_names:
            story.append(Paragraph(escape(name), styles["Normal"]))
    else:
        story.append(Paragraph("Keine Teilnehmer eingetragen.", styles["Normal"]))
    story.append(Spacer(1, 5 * mm))
    for entry in entries:
        safe_text = escape(entry["text"] or "—").replace("\n", "<br/>")
        story.append(KeepTogether([
            Paragraph(escape(entry["title"]), styles["ProtocolTopic"]),
            Paragraph(safe_text, styles["Normal"]),
            Paragraph(f"<i>Status: {escape(entry['status'])}</i>", styles["Normal"]),
        ]))
    if not entries:
        story.append(Paragraph("Keine Tagesordnungspunkte.", styles["Normal"]))

    def add_page_number(canvas, doc):
        canvas.saveState()
        canvas.setFont(regular_font, 8)
        canvas.setFillColor(colors.grey)
        canvas.drawRightString(A4[0] - 20 * mm, 10 * mm, f"Seite {doc.page}")
        canvas.restoreState()

    document.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
    response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{_protocol_filename(meeting, "pdf")}"'
    return response


@login_required
def protocol_docx(request, pk):
    meeting = get_object_or_404(Meeting.objects.select_related("series"), pk=pk)
    entries = _protocol_entries(meeting)

    from docx import Document
    from docx.shared import Pt, RGBColor

    document = Document()
    document.core_properties.title = f"Protokoll – {meeting.series.name}"
    document.core_properties.subject = f"Besprechung vom {meeting.date:%d.%m.%Y}"
    document.add_heading("Protokoll", 0)
    document.add_heading(meeting.series.name, level=1)
    document.add_paragraph(f"Datum: {meeting.date:%d.%m.%Y}")
    document.add_paragraph(
        f"Gesicherter Stand: {meeting.finalized_at:%d.%m.%Y %H:%M}"
        if meeting.finalized_at else "Entwurf – nicht abgeschlossen"
    )
    document.add_heading("Teilnehmer", level=2)
    participant_names = _meeting_participant_names(meeting)
    if participant_names:
        for name in participant_names:
            document.add_paragraph(name, style="List Bullet")
    else:
        document.add_paragraph("Keine Teilnehmer eingetragen.")
    for entry in entries:
        document.add_heading(entry["title"], level=2)
        document.add_paragraph(entry["text"] or "—")
        status = document.add_paragraph()
        run = status.add_run(f"Status: {entry['status']}")
        run.italic = True
        run.font.size = Pt(9)
        run.font.color.rgb = RGBColor(100, 100, 100)
    if not entries:
        document.add_paragraph("Keine Tagesordnungspunkte.")

    buffer = BytesIO()
    document.save(buffer)
    response = HttpResponse(
        buffer.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
    response["Content-Disposition"] = f'attachment; filename="{_protocol_filename(meeting, "docx")}"'
    return response


@login_required
def protocol(request, pk):
    meeting = get_object_or_404(Meeting, pk=pk)
    ensure_agenda(meeting)
    snapshots = meeting.snapshots.all()
    participants = meeting.participants.filter(is_active=True).order_by("last_name", "first_name", "username")
    return render(request, "meetings/protocol.html", {
        "meeting": meeting, "snapshots": snapshots, "participants": participants,
    })

@login_required
@user_passes_test(admin_only)
def series_admin(request):
    series = MeetingSeries.objects.all()
    form = SeriesForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        item = form.save()
        generate_meetings(item)
        messages.success(request, "Besprechungsreihe und Termine angelegt.")
        return redirect("series_admin")
    return render(request, "meetings/series.html", {"series": series, "form": form})

@login_required
@user_passes_test(admin_only)
def finalize(request, pk):
    if request.method != "POST":
        return HttpResponseForbidden()
    meeting = get_object_or_404(Meeting, pk=pk)
    finalize_meeting(meeting)
    record_event(actor=request.user, action="finalized",
                 summary=f"Besprechung „{meeting.series.name}“ vom {meeting.date:%d.%m.%Y} abgeschlossen",
                 meeting=meeting, changes={"Abgeschlossen": {"vorher": None, "nachher": meeting.finalized_at.isoformat()}})
    messages.success(request, "Besprechung abgeschlossen; Protokoll-Snapshot gespeichert.")
    return redirect("protocol", pk=pk)


@login_required
def audit_history(request):
    events = AuditEvent.objects.select_related("actor", "topic", "meeting", "meeting__series")
    topic_id = request.GET.get("topic")
    if topic_id:
        events = events.filter(topic_id=topic_id)
    return render(request, "meetings/audit_history.html", {
        "events": events[:250], "selected_topic": topic_id,
        "topics": Topic.objects.order_by("title"),
    })


@login_required
def topic_comment_add(request, pk):
    topic = get_object_or_404(Topic, pk=pk)
    if request.method != "POST":
        return redirect("topic_edit", pk=pk)
    form = TopicCommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.topic = topic
        comment.author = request.user
        comment.save()
        record_event(actor=request.user, action="comment_added",
            summary=f"Kommentar zu „{topic.title}“ hinzugefügt", topic=topic,
            changes={"Kommentar": comment.body[:500]})
        messages.success(request, "Kommentar hinzugefügt.")
    else:
        messages.error(request, "Bitte gib einen Kommentar ein (maximal 5.000 Zeichen).")
    return redirect("topic_edit", pk=pk)
