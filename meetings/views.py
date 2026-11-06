from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from .forms import UsernameLoginForm, TopicForm, AgendaTextForm, AttachmentForm, SeriesForm, MeetingForm, MeetingDateForm
from .models import Meeting, MeetingSeries, Topic, TopicAttachment, TopicTransferHistory
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
                form.save()
                messages.success(request, "Agendatext gespeichert.")
        return redirect("meeting", pk=pk)
    return render(request, "meetings/meeting.html", {"meeting": meeting, "items": items})

@login_required
def topic_edit(request, pk):
    topic = get_object_or_404(Topic, pk=pk)
    form = TopicForm(request.POST or None, instance=topic)
    if request.method == "POST" and form.is_valid():
        old_series = topic.series
        updated_topic = form.save(commit=False)
        new_series = updated_topic.series
        with transaction.atomic():
            if old_series != new_series:
                TopicTransferHistory.objects.create(
                    topic=topic, from_series=old_series, to_series=new_series,
                    transferred_by=request.user, note="Zuordnung im Themenformular geändert",
                )
            updated_topic.save()
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
        messages.success(request, "Thema wurde archiviert.")
    return redirect("archive")

@login_required
def topic_reopen(request, pk):
    if request.method != "POST":
        return HttpResponseForbidden()
    topic = get_object_or_404(Topic, pk=pk, status="archived")
    topic.status = "open"
    topic.save(update_fields=["status", "updated_at"])
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
        topic.series = target
        topic.save(update_fields=["series", "updated_at"])
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
    messages.success(request, "Besprechung abgeschlossen; Protokoll-Snapshot gespeichert.")
    return redirect("protocol", pk=pk)
