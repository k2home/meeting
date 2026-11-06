from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from .forms import UsernameLoginForm, TopicForm, TopicCommentForm, AgendaTextForm, AttachmentForm, SeriesForm
from .models import Meeting, MeetingSeries, Topic, TopicAttachment, TopicTransferHistory, AuditEvent
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

def admin_only(user):
    return user.is_authenticated and user.is_staff

@login_required
def dashboard(request):
    today = timezone.localdate()
    meetings = Meeting.objects.filter(date__gte=today).select_related("series").order_by("date")[:20]
    topics = Topic.objects.filter(status="open").select_related("series")
    overdue_count = topics.filter(due_date__lt=today).count()
    return render(request, "meetings/dashboard.html", {
        "meetings": meetings, "topics": topics, "overdue_count": overdue_count, "today": today,
    })

@login_required
def meeting_detail(request, pk):
    meeting = get_object_or_404(Meeting.objects.select_related("series"), pk=pk)
    items = ensure_agenda(meeting)
    if request.method == "POST" and not meeting.finalized_at:
        item_id = request.POST.get("item_id")
        if item_id:
            from .models import AgendaItem
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
    return render(request, "meetings/meeting.html", {"meeting": meeting, "items": items})

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

@login_required
def protocol(request, pk):
    meeting = get_object_or_404(Meeting, pk=pk)
    ensure_agenda(meeting)
    snapshots = meeting.snapshots.all()
    return render(request, "meetings/protocol.html", {"meeting": meeting, "snapshots": snapshots})

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
