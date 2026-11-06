from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from .forms import UsernameLoginForm, TopicForm, AgendaTextForm, AttachmentForm, SeriesForm
from .models import Meeting, MeetingSeries, Topic, TopicAttachment
from .services import ensure_agenda, generate_meetings, finalize_meeting

def login_view(request):
    if request.user.is_authenticated: return redirect("dashboard")
    form = UsernameLoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        from django.contrib.auth import get_user_model
        User = get_user_model()
        username = form.cleaned_data["username"].strip()
        user, _ = User.objects.get_or_create(username=username, defaults={"is_active": True})
        login(request, user, backend="django.contrib.auth.backends.ModelBackend")
        return redirect("dashboard")
    return render(request, "meetings/login.html", {"form":form})

def logout_view(request):
    logout(request)
    return redirect("login")

def admin_only(user): return user.is_authenticated and user.is_staff

@login_required
def dashboard(request):
    meetings = Meeting.objects.filter(date__gte=timezone.localdate()).select_related("series").order_by("date")[:20]
    topics = Topic.objects.filter(status="open").select_related("series")
    return render(request,"meetings/dashboard.html",{"meetings":meetings,"topics":topics})

@login_required
def meeting_detail(request, pk):
    meeting = get_object_or_404(Meeting.objects.select_related("series"),pk=pk)
    items = ensure_agenda(meeting)
    if request.method == "POST" and not meeting.finalized_at:
        item_id = request.POST.get("item_id")
        if item_id:
            from .models import AgendaItem
            item = get_object_or_404(AgendaItem,pk=item_id,meeting=meeting)
            form = AgendaTextForm(request.POST,instance=item)
            if form.is_valid(): form.save(); messages.success(request,"Agendatext gespeichert.")
        return redirect("meeting",pk=pk)
    return render(request,"meetings/meeting.html",{"meeting":meeting,"items":items})

@login_required
def topic_edit(request, pk):
    topic = get_object_or_404(Topic,pk=pk)
    form = TopicForm(request.POST or None,instance=topic)
    if request.method == "POST" and form.is_valid():
        form.save(); messages.success(request,"Thema gespeichert."); return redirect("dashboard")
    return render(request,"meetings/topic_form.html",{"form":form,"topic":topic})

@login_required
def topic_new(request):
    form = TopicForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        topic=form.save(); return redirect("topic_edit",pk=topic.pk)
    return render(request,"meetings/topic_form.html",{"form":form})

@login_required
def attachment_add(request, pk):
    topic=get_object_or_404(Topic,pk=pk)
    form=AttachmentForm(request.POST or None,request.FILES or None)
    if request.method=="POST" and form.is_valid():
        obj=form.save(commit=False); obj.topic=topic; obj.save(); return redirect("topic_edit",pk=pk)
    return render(request,"meetings/attachment_form.html",{"form":form,"topic":topic})

@login_required
def protocol(request, pk):
    meeting=get_object_or_404(Meeting,pk=pk)
    ensure_agenda(meeting)
    snapshots=meeting.snapshots.all()
    return render(request,"meetings/protocol.html",{"meeting":meeting,"snapshots":snapshots})

@login_required
@user_passes_test(admin_only)
def series_admin(request):
    series=MeetingSeries.objects.all()
    form=SeriesForm(request.POST or None)
    if request.method=="POST" and form.is_valid():
        item=form.save(); generate_meetings(item); messages.success(request,"Besprechungsreihe und Termine angelegt."); return redirect("series_admin")
    return render(request,"meetings/series.html",{"series":series,"form":form})

@login_required
@user_passes_test(admin_only)
def finalize(request, pk):
    if request.method != "POST": return HttpResponseForbidden()
    meeting=get_object_or_404(Meeting,pk=pk); finalize_meeting(meeting)
    messages.success(request,"Besprechung abgeschlossen; Protokoll-Snapshot gespeichert.")
    return redirect("protocol",pk=pk)
