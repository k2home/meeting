from datetime import date, timedelta
from functools import wraps
from io import BytesIO
from pathlib import Path
from urllib.parse import quote, urlencode
from xml.sax.saxutils import escape

from django.contrib import messages
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import F, Q, Window, Prefetch, Min
from django.db.models.functions import RowNumber
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.utils.http import url_has_allowed_host_and_scheme
from .forms import UsernameLoginForm, TopicForm, TopicCommentForm, AgendaTextForm, AttachmentForm, SeriesForm, MeetingParticipantsForm, MeetingDateForm, AgendaItemCreateForm, AgendaScheduleForm
from .models import Meeting, MeetingSeries, Topic, TopicAttachment, TopicTransferHistory, AuditEvent, AgendaItem, OrganizationSettings
from .audit import record_event
from .services import ensure_agenda, generate_meetings, finalize_meeting
from .access import accessible_meetings, accessible_series, accessible_topics, has_writable_series, is_admin, is_moderator, is_reader
from .models import SeriesAccess
from .user_display import user_display_name

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


def _series_for_view(view, kwargs):
    pk = kwargs.get("pk")
    if not pk:
        return None
    if view.__name__ in {"agenda_reorder", "meeting_detail", "meeting_edit", "meeting_delete", "meeting_reopen"}:
        meeting = Meeting.objects.filter(pk=pk).select_related("series").first()
        return meeting.series if meeting else None
    if view.__name__ in {"series_edit", "series_delete", "series_extend", "series_reset_meetings"}:
        return MeetingSeries.objects.filter(pk=pk).first()
    topic = Topic.objects.filter(pk=pk).select_related("series").first()
    return topic.series if topic else None


def moderator_required(view):
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        series = _series_for_view(view, kwargs)
        allowed = is_admin(request.user) or (
            is_moderator(request.user, series) if series is not None
            else is_moderator(request.user)
        )
        if not allowed:
            return HttpResponseForbidden("Für diese Besprechungsreihe fehlen Moderatorrechte.")
        return view(request, *args, **kwargs)
    return wrapped


def reader_readonly(view):
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        if is_reader(request.user, _series_for_view(view, kwargs)) and request.method == "POST":
            return HttpResponseForbidden("Leser*innen haben ausschließlich Leserechte.")
        return view(request, *args, **kwargs)
    return wrapped


def reader_no_access(view):
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        series = _series_for_view(view, kwargs)
        if (series is not None and is_reader(request.user, series)) or (
            series is None and not has_writable_series(request.user)
        ):
            return HttpResponseForbidden("Für diese Besprechungsreihe bestehen ausschließlich Leserechte.")
        return view(request, *args, **kwargs)
    return wrapped


def admin_only(user):
    return is_admin(user)

@login_required
def dashboard(request):
    today = timezone.localdate()
    meetings = (
        accessible_meetings(request.user).filter(date__gte=today, series__isnull=False)
        .annotate(series_position=Window(
            expression=RowNumber(),
            partition_by=[F("series_id")],
            order_by=[F("date").asc(), F("pk").asc()],
        ))
        .filter(series_position__lte=2)
        .select_related("series")
        .order_by("date", "series__name", "pk")
    )
    topics = accessible_topics(request.user).select_related("series", "assigned_to")
    query = request.GET.get("q", "").strip()
    selected_status = request.GET.get("status", "all" if is_reader(request.user) and not has_writable_series(request.user) else "open")
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
            | Q(agenda_items__assigned_to__username__icontains=query)
            | Q(agenda_items__assigned_to__first_name__icontains=query)
            | Q(agenda_items__assigned_to__last_name__icontains=query)
        )
    if selected_series.isdigit():
        topics = topics.filter(series_id=int(selected_series))
    else:
        selected_series = ""
    if selected_assignee == "unassigned":
        topics = topics.filter(assigned_to__isnull=True).exclude(agenda_items__assigned_to__isnull=False)
    elif selected_assignee.isdigit():
        topics = topics.filter(Q(assigned_to_id=int(selected_assignee)) | Q(agenda_items__assigned_to_id=int(selected_assignee))).distinct()
    else:
        selected_assignee = ""
    topics = topics.annotate(next_meeting_date=Min("agenda_items__meeting__date", filter=Q(agenda_items__meeting__finalized_at__isnull=True)))
    if selected_due == "overdue":
        topics = topics.filter(next_meeting_date__lt=today, status="open")
    elif selected_due == "today":
        topics = topics.filter(next_meeting_date=today)
    elif selected_due == "without_date":
        topics = topics.filter(next_meeting_date__isnull=True)
    elif selected_due == "future":
        topics = topics.filter(next_meeting_date__gt=today)

    overdue_count = accessible_topics(request.user).filter(status="open", agenda_items__meeting__date__lt=today, agenda_items__meeting__finalized_at__isnull=True).distinct().count()
    return render(request, "meetings/dashboard.html", {
        "meetings": meetings, "topics": topics, "overdue_count": overdue_count, "today": today,
        "query": query, "selected_status": selected_status, "selected_series": selected_series,
        "selected_assignee": selected_assignee, "selected_due": selected_due,
        "series_options": accessible_series(request.user).order_by("name"),
        "assignee_options": UserModel.objects.filter(is_active=True).order_by("username"),
        "result_count": topics.count(),
    })


@login_required
def open_topics(request):
    """List non-completed topics without a future agenda appointment."""
    today = timezone.localdate()
    if is_admin(request.user):
        allowed_series = MeetingSeries.objects.all()
    else:
        allowed_series = MeetingSeries.objects.filter(
            user_access__user=request.user,
            user_access__role__in=[SeriesAccess.ROLE_PARTICIPANT, SeriesAccess.ROLE_MODERATOR],
        ).distinct()
        if not allowed_series.exists():
            return HttpResponseForbidden("Für diese Funktion ist eine Teilnehmer- oder Moderatorrolle erforderlich.")

    topics = (
        Topic.objects.filter(series__in=allowed_series)
        .exclude(status="done")
        .exclude(agenda_items__meeting__date__gt=today)
        .select_related("series", "assigned_to")
        .distinct()
        .order_by("series__name", "title")
    )
    if request.method == "POST":
        topic = get_object_or_404(topics, pk=request.POST.get("schedule_topic"))
        target_meeting = get_object_or_404(
            Meeting.objects.filter(series=topic.series, date__gt=today, finalized_at__isnull=True),
            pk=request.POST.get("target_meeting"),
        )
        with transaction.atomic():
            next_position = (
                target_meeting.agenda_items.order_by("-position").values_list("position", flat=True).first()
                if target_meeting.agenda_items.exists() else -1
            ) + 1
            AgendaItem.objects.get_or_create(
                meeting=target_meeting,
                topic=topic,
                defaults={"working_text": "", "position": next_position},
            )
            record_event(
                actor=request.user,
                action="updated",
                summary=f"„{topic.title}“ auf die Tagesordnung am {target_meeting.date:%d.%m.%Y} gesetzt",
                topic=topic,
                meeting=target_meeting,
                changes={"Wiedervorlage": {"nachher": target_meeting.date.isoformat()}},
            )
        messages.success(request, f"„{topic.title}“ wurde auf die Tagesordnung am {target_meeting.date:%d.%m.%Y} gesetzt.")
        return redirect("open_topics")

    rows = []
    for topic in topics:
        future_meetings = Meeting.objects.filter(
            series=topic.series, date__gt=today, finalized_at__isnull=True
        ).order_by("date")
        rows.append({"topic": topic, "future_meetings": future_meetings})
    return render(request, "meetings/open_topics.html", {"rows": rows, "today": today})

@login_required
def my_tasks(request):
    """Show open topics assigned to the user either at topic or agenda-item level."""
    today = timezone.localdate()
    responsibility = (
        Q(assigned_to=request.user, agenda_items__isnull=True)
        | Q(assigned_to=request.user, agenda_items__assigned_to__isnull=True)
        | Q(agenda_items__assigned_to=request.user)
    )
    topics = accessible_topics(request.user).filter(responsibility, status="open").select_related("series").annotate(
        next_meeting_date=Min(
            "agenda_items__meeting__date",
            filter=Q(agenda_items__meeting__finalized_at__isnull=True)
            & (Q(agenda_items__assigned_to=request.user) | Q(agenda_items__assigned_to__isnull=True, assigned_to=request.user)),
        )
    ).distinct().order_by(F("next_meeting_date").asc(nulls_last=True), "title")
    return render(request, "meetings/my_tasks.html", {
        "topics": topics, "today": today,
        "overdue_count": topics.filter(next_meeting_date__lt=today).count(),
        "due_today_count": topics.filter(next_meeting_date=today).count(),
        "without_due_date_count": topics.filter(next_meeting_date__isnull=True).count(),
    })

@login_required
@reader_readonly
def agenda_reorder(request, pk):
    if request.method != "POST":
        return HttpResponseForbidden()
    meeting = get_object_or_404(accessible_meetings(request.user), pk=pk)
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
@reader_readonly
def meeting_detail(request, pk):
    meeting = get_object_or_404(accessible_meetings(request.user).select_related("series"), pk=pk)
    if not meeting.participants_initialized:
        if not meeting.participants.exists() and meeting.series_id:
            default_participants = SeriesAccess.objects.filter(
                series=meeting.series, user__is_active=True
            ).exclude(role=SeriesAccess.ROLE_READER).values_list("user_id", flat=True)
            meeting.participants.set(default_participants)
        meeting.participants_initialized = True
        meeting.save(update_fields=["participants_initialized"])
    items = ensure_agenda(meeting)
    participants = meeting.participants.filter(is_active=True).order_by("last_name", "first_name", "username")
    assignees = UserModel.objects.filter(is_active=True).order_by("last_name", "first_name", "username")
    writable_series = accessible_series(request.user)
    if not is_admin(request.user):
        writable_series = writable_series.exclude(user_access__role=SeriesAccess.ROLE_READER)
    writable_series = writable_series.filter(active=True).order_by("name")
    target_meetings = accessible_meetings(request.user).filter(
        series__in=writable_series, date__gt=meeting.date, finalized_at__isnull=True
    ).select_related("series").order_by("series__name", "date")

    if request.method == "POST":
        if meeting.finalized_at:
            messages.error(request, "Eine abgeschlossene Besprechung kann nicht mehr geändert werden.")
            return redirect("meeting", pk=pk)
        if request.POST.get("save_participants"):
            before = [user_display_name(u) for u in meeting.participants.all()]
            participant_form = MeetingParticipantsForm(request.POST, instance=meeting)
            if participant_form.is_valid():
                participant_form.save()
                meeting.participants_initialized = True
                meeting.save(update_fields=["participants_initialized"])
                after = [user_display_name(u) for u in meeting.participants.all()]
                if before != after:
                    record_event(
                        actor=request.user, action="updated",
                        summary=f"Teilnehmerliste für „{_meeting_series_name(meeting)}“ am {meeting.date:%d.%m.%Y} geändert",
                        meeting=meeting,
                        changes={"Teilnehmer": {"vorher": before, "nachher": after}},
                    )
                messages.success(request, "Teilnehmerliste gespeichert.")
            else:
                messages.error(request, "Bitte prüfe die Teilnehmerauswahl.")
                return render(request, "meetings/meeting.html", {
                    "meeting": meeting, "items": items, "participant_form": participant_form,
                    "participants": participants, "assignees": assignees, "is_reader": is_reader(request.user, meeting.series),
                    "is_moderator": is_moderator(request.user, meeting.series),
                    "writable_series": writable_series, "target_meetings": target_meetings,
                })
        elif request.POST.get("shift_item"):
            item = get_object_or_404(AgendaItem.objects.select_related("topic"), pk=request.POST.get("shift_item"), meeting=meeting)
            schedule_form = AgendaScheduleForm(
                request.POST, series_queryset=writable_series, meeting_queryset=target_meetings,
            )
            if schedule_form.is_valid():
                topic = item.topic
                old_series = topic.series
                target_series = schedule_form.cleaned_data["target_series"]
                target_meeting = schedule_form.cleaned_data["target_meeting"]
                if target_meeting.pk == meeting.pk:
                    messages.error(request, "Bitte wähle einen anderen, späteren Besprechungstermin.")
                else:
                    target_item = AgendaItem.objects.filter(meeting=target_meeting, topic=topic).first()
                    if target_item:
                        target_item.working_text = item.working_text
                        target_item.position = (target_meeting.agenda_items.exclude(pk=target_item.pk).order_by("-position").values_list("position", flat=True).first() if target_meeting.agenda_items.exclude(pk=target_item.pk).exists() else -1) + 1
                        target_item.save(update_fields=["working_text", "position"])
                        if item.assigned_to_id and not target_item.assigned_to_id:
                            target_item.assigned_to_id = item.assigned_to_id
                            target_item.save(update_fields=["assigned_to"])
                        item.delete()
                    else:
                        next_position = (target_meeting.agenda_items.order_by("-position").values_list("position", flat=True).first() if target_meeting.agenda_items.exists() else -1) + 1
                        item.meeting = target_meeting
                        item.position = next_position
                        item.save(update_fields=["meeting", "position"])
                    topic.series = target_series
                    topic.save(update_fields=["series", "updated_at"])
                    if old_series != target_series:
                        TopicTransferHistory.objects.create(
                            topic=topic, from_series=old_series, to_series=target_series,
                            transferred_by=request.user,
                            note=f"Agenda-Punkt ohne Besprechung auf {target_meeting.date:%d.%m.%Y} verschoben",
                        )
                    record_event(
                        actor=request.user, action="transferred" if old_series != target_series else "updated",
                        summary=f"„{topic.title}“ ohne Besprechung von {meeting.date:%d.%m.%Y} auf {target_series.name} am {target_meeting.date:%d.%m.%Y} verschoben",
                        topic=topic, meeting=meeting,
                        changes={
                            "Tagesordnung": {"vorher": meeting.date.isoformat(), "nachher": target_meeting.date.isoformat()},
                            "Wiedervorlage": {"nachher": target_meeting.date.isoformat()},
                            "Besprechungsserie": {
                                "vorher": old_series.name if old_series else None,
                                "nachher": target_series.name,
                            },
                        },
                    )
                    messages.success(request, f"„{topic.title}“ wurde aus dieser Tagesordnung entfernt und auf den {target_meeting.date:%d.%m.%Y} verschoben.")
            else:
                messages.error(request, "Bitte wähle eine gültige Besprechungsserie und einen dazugehörigen späteren Termin.")
        elif request.POST.get("schedule_item") and not request.POST.get("item_id"):
            item = get_object_or_404(AgendaItem, pk=request.POST.get("schedule_item"), meeting=meeting)
            schedule_form = AgendaScheduleForm(
                request.POST, series_queryset=writable_series, meeting_queryset=target_meetings,
            )
            if schedule_form.is_valid():
                topic = item.topic
                old_series = topic.series
                target_series = schedule_form.cleaned_data["target_series"]
                target_meeting = schedule_form.cleaned_data["target_meeting"]
                topic.series = target_series
                topic.save(update_fields=["series", "updated_at"])
                next_position = (target_meeting.agenda_items.order_by("-position").values_list("position", flat=True).first() if target_meeting.agenda_items.exists() else -1) + 1
                target_item, created = AgendaItem.objects.get_or_create(
                    meeting=target_meeting, topic=topic,
                    defaults={"working_text": "", "position": next_position, "assigned_to_id": item.assigned_to_id},
                )
                if not created and target_item.working_text:
                    target_item.working_text = ""
                    target_item.save(update_fields=["working_text"])
                if not created and item.assigned_to_id and not target_item.assigned_to_id:
                    target_item.assigned_to_id = item.assigned_to_id
                    target_item.save(update_fields=["assigned_to"])
                if old_series != target_series:
                    TopicTransferHistory.objects.create(
                        topic=topic, from_series=old_series, to_series=target_series,
                        transferred_by=request.user,
                        note=f"Wiedervorlage für {target_meeting.date:%d.%m.%Y} festgelegt",
                    )
                record_event(
                    actor=request.user, action="transferred" if old_series != target_series else "updated",
                    summary=f"Wiedervorlage für „{topic.title}“ auf {target_series.name} am {target_meeting.date:%d.%m.%Y} gesetzt",
                    topic=topic, meeting=meeting,
                    changes={
                        "Wiedervorlage": {"nachher": target_meeting.date.isoformat()},
                        "Besprechungsserie": {
                            "vorher": old_series.name if old_series else None,
                            "nachher": target_series.name,
                        },
                    },
                )
                messages.success(request, f"„{topic.title}“ steht am {target_meeting.date:%d.%m.%Y} erneut auf der Tagesordnung von {target_series.name}.")
            else:
                messages.error(request, "Bitte wähle eine gültige Besprechungsserie und einen dazugehörigen Termin.")
        elif request.POST.get("update_agenda_assignee"):
            item = get_object_or_404(AgendaItem, pk=request.POST.get("update_agenda_assignee"), meeting=meeting)
            assignee_id = request.POST.get("assigned_to") or None
            assignee = get_object_or_404(UserModel, pk=assignee_id, is_active=True) if assignee_id else None
            if item.assigned_to_id != (assignee.pk if assignee else None):
                old_assignee = user_display_name(item.assigned_to) if item.assigned_to else "Hauptverantwortliche Person"
                item.assigned_to = assignee
                item.save(update_fields=["assigned_to"])
                new_assignee = user_display_name(assignee) if assignee else "Hauptverantwortliche Person"
                record_event(
                    actor=request.user, action="updated",
                    summary=f"Abweichende Zuständigkeit für „{item.topic.title}“ geändert",
                    topic=item.topic, meeting=meeting,
                    changes={"Zuständigkeit Tagesordnungspunkt": {"vorher": old_assignee, "nachher": new_assignee}},
                )
                messages.success(request, "Zuständigkeit des Tagesordnungspunkts gespeichert.")
            else:
                messages.info(request, "Die Zuständigkeit ist unverändert.")
        elif request.POST.get("update_topic_status"):
            item = get_object_or_404(AgendaItem, pk=request.POST.get("update_topic_status"), meeting=meeting)
            new_status = request.POST.get("status")
            valid_statuses = dict(Topic.STATUS)
            if new_status not in valid_statuses:
                messages.error(request, "Bitte wähle einen gültigen Themenstatus.")
            elif item.topic.status != new_status:
                old_status = item.topic.get_status_display()
                item.topic.status = new_status
                item.topic.save(update_fields=["status", "updated_at"])
                record_event(
                    actor=request.user, action="updated",
                    summary=f"Status für „{item.topic.title}“ auf {valid_statuses[new_status]} gesetzt",
                    topic=item.topic, meeting=meeting,
                    changes={"Status": {"vorher": old_status, "nachher": valid_statuses[new_status]}},
                )
                messages.success(request, "Themenstatus gespeichert.")
            else:
                messages.info(request, "Der Themenstatus ist unverändert.")
        elif request.POST.get("add_existing_topic"):
            topic = get_object_or_404(accessible_topics(request.user), pk=request.POST.get("add_existing_topic"))
            if meeting.agenda_items.filter(topic=topic).exists():
                messages.info(request, f"„{topic.title}“ steht bereits auf dieser Tagesordnung.")
            else:
                AgendaItem.objects.create(
                    meeting=meeting, topic=topic, working_text=topic.description,
                    position=(meeting.agenda_items.order_by("-position").values_list("position", flat=True).first() if meeting.agenda_items.exists() else -1) + 1,
                )
                record_event(
                    actor=request.user, action="created",
                    summary=f"Vorhandenes Thema „{topic.title}“ in die Tagesordnung am {meeting.date:%d.%m.%Y} übernommen",
                    topic=topic, meeting=meeting,
                    changes={"Tagesordnung": {"vorher": None, "nachher": meeting.date.isoformat()}},
                )
                messages.success(request, f"„{topic.title}“ wurde in diese Tagesordnung übernommen. Terminserie und Wiedervorlage des Themas bleiben unverändert.")
        elif request.POST.get("add_agenda_topic"):
            create_form = AgendaItemCreateForm(request.POST)
            if create_form.is_valid():
                title = create_form.cleaned_data["title"].strip()
                working_text = create_form.cleaned_data["working_text"]
                if not title:
                    messages.error(request, "Bitte gib einen Thementitel ein.")
                else:
                    topic = Topic.objects.create(
                        title=title, description=working_text, series=meeting.series,
                    )
                    AgendaItem.objects.create(
                        meeting=meeting, topic=topic, working_text=working_text,
                        assigned_to=create_form.cleaned_data["assigned_to"],
                        position=(meeting.agenda_items.order_by("-position").values_list("position", flat=True).first() if meeting.agenda_items.exists() else -1) + 1,
                    )
                    record_event(
                        actor=request.user, action="created",
                        summary=f"Thema „{topic.title}“ zur Tagesordnung am {meeting.date:%d.%m.%Y} hinzugefügt",
                        topic=topic, meeting=meeting,
                        changes={"Titel": {"vorher": None, "nachher": topic.title}},
                    )
                    messages.success(request, f"„{topic.title}“ wurde neu angelegt und zur Tagesordnung hinzugefügt.")
            else:
                messages.error(request, "Bitte prüfe den Titel des neuen Themas.")
        elif request.POST.get("save_all_working_texts"):
            changed_count = 0
            for agenda_item in items:
                field_name = f"working_text_{agenda_item.pk}"
                if field_name not in request.POST:
                    continue
                new_text = request.POST.get(field_name, "")
                old_text = agenda_item.working_text
                if old_text == new_text:
                    continue
                agenda_item.working_text = new_text
                agenda_item.save(update_fields=["working_text"])
                record_event(
                    actor=request.user, action="agenda_edited",
                    summary=f"Agendatext für „{agenda_item.topic.title}“ in {meeting.date:%d.%m.%Y} geändert",
                    topic=agenda_item.topic, meeting=meeting,
                    changes={"Text": {"vorher": old_text, "nachher": new_text}},
                )
                changed_count += 1
            if request.POST.get("schedule_item"):
                scheduled_item = get_object_or_404(
                    AgendaItem.objects.select_related("topic", "topic__series"),
                    pk=request.POST.get("schedule_item"), meeting=meeting,
                )
                schedule_form = AgendaScheduleForm(
                    request.POST, series_queryset=writable_series, meeting_queryset=target_meetings,
                )
                if schedule_form.is_valid():
                    topic = scheduled_item.topic
                    old_series = topic.series
                    target_series = schedule_form.cleaned_data["target_series"]
                    target_meeting = schedule_form.cleaned_data["target_meeting"]
                    topic.series = target_series
                    topic.save(update_fields=["series", "updated_at"])
                    next_position = (target_meeting.agenda_items.order_by("-position").values_list("position", flat=True).first() if target_meeting.agenda_items.exists() else -1) + 1
                    target_item, created = AgendaItem.objects.get_or_create(
                        meeting=target_meeting, topic=topic,
                        defaults={"working_text": "", "position": next_position, "assigned_to_id": scheduled_item.assigned_to_id},
                    )
                    if not created and target_item.working_text:
                        target_item.working_text = ""
                        target_item.save(update_fields=["working_text"])
                    if not created and scheduled_item.assigned_to_id and not target_item.assigned_to_id:
                        target_item.assigned_to_id = scheduled_item.assigned_to_id
                        target_item.save(update_fields=["assigned_to"])
                    if old_series != target_series:
                        TopicTransferHistory.objects.create(
                            topic=topic, from_series=old_series, to_series=target_series,
                            transferred_by=request.user,
                            note=f"Wiedervorlage für {target_meeting.date:%d.%m.%Y} festgelegt",
                        )
                    record_event(
                        actor=request.user, action="transferred" if old_series != target_series else "updated",
                        summary=f"Wiedervorlage für „{topic.title}“ auf {target_series.name} am {target_meeting.date:%d.%m.%Y} gesetzt",
                        topic=topic, meeting=meeting,
                        changes={
                            "Wiedervorlage": {"nachher": target_meeting.date.isoformat()},
                            "Besprechungsserie": {
                                "vorher": old_series.name if old_series else None,
                                "nachher": target_series.name,
                            },
                        },
                    )
                else:
                    messages.error(request, "Bitte wähle eine gültige Besprechungsserie und einen dazugehörigen Termin.")
            messages.success(request, f"{changed_count} geänderte Tagesordnungspunkte gespeichert.")
        else:
            item_id = request.POST.get("item_id")
            if item_id:
                item = get_object_or_404(AgendaItem.objects.select_related("topic", "topic__series"), pk=item_id, meeting=meeting)
                form = AgendaTextForm(request.POST, instance=item)
                schedule_form = None
                if request.POST.get("schedule_item") == str(item.pk):
                    schedule_form = AgendaScheduleForm(
                        request.POST, series_queryset=writable_series, meeting_queryset=target_meetings,
                    )
                if form.is_valid() and (schedule_form is None or schedule_form.is_valid()):
                    old_text = item.working_text
                    with transaction.atomic():
                        saved = form.save()
                        if old_text != saved.working_text:
                            record_event(actor=request.user, action="agenda_edited",
                                summary=f"Agendatext für „{item.topic.title}“ in {meeting.date:%d.%m.%Y} geändert",
                                topic=item.topic, meeting=meeting,
                                changes={"Text": {"vorher": old_text, "nachher": saved.working_text}})
                        if schedule_form is not None:
                            topic = item.topic
                            old_series = topic.series
                            target_series = schedule_form.cleaned_data["target_series"]
                            target_meeting = schedule_form.cleaned_data["target_meeting"]
                            topic.series = target_series
                            topic.save(update_fields=["series", "updated_at"])
                            next_position = (target_meeting.agenda_items.order_by("-position").values_list("position", flat=True).first() if target_meeting.agenda_items.exists() else -1) + 1
                            target_item, created = AgendaItem.objects.get_or_create(
                                meeting=target_meeting, topic=topic,
                                defaults={"working_text": "", "position": next_position, "assigned_to_id": item.assigned_to_id},
                            )
                            if not created and target_item.working_text:
                                target_item.working_text = ""
                                target_item.save(update_fields=["working_text"])
                            if not created and item.assigned_to_id and not target_item.assigned_to_id:
                                target_item.assigned_to_id = item.assigned_to_id
                                target_item.save(update_fields=["assigned_to"])
                            if old_series != target_series:
                                TopicTransferHistory.objects.create(
                                    topic=topic, from_series=old_series, to_series=target_series,
                                    transferred_by=request.user,
                                    note=f"Wiedervorlage für {target_meeting.date:%d.%m.%Y} festgelegt",
                                )
                            record_event(
                                actor=request.user, action="transferred" if old_series != target_series else "updated",
                                summary=f"Wiedervorlage für „{topic.title}“ auf {target_series.name} am {target_meeting.date:%d.%m.%Y} gesetzt",
                                topic=topic, meeting=meeting,
                                changes={
                                    "Wiedervorlage": {"nachher": target_meeting.date.isoformat()},
                                    "Besprechungsserie": {
                                        "vorher": old_series.name if old_series else None,
                                        "nachher": target_series.name,
                                    },
                                },
                            )
                    messages.success(request, "Agendatext und Wiedervorlage gespeichert." if schedule_form is not None else "Agendatext gespeichert.")
                else:
                    messages.error(request, "Bitte prüfe den Text und die ausgewählte Wiedervorlage.")
        if request.POST.get("item_id") and not request.POST.get("save_all_working_texts"):
            return redirect(reverse("meeting", args=[pk]) + f"#agenda-item-{request.POST.get('item_id')}")
        return redirect("meeting", pk=pk)

    participant_form = MeetingParticipantsForm(instance=meeting)
    return render(request, "meetings/meeting.html", {
        "meeting": meeting, "items": items, "participant_form": participant_form,
        "participants": participants, "assignees": assignees, "is_reader": is_reader(request.user, meeting.series),
        "is_moderator": is_moderator(request.user, meeting.series),
        "writable_series": writable_series, "target_meetings": target_meetings,
    })


@login_required
def topic_suggestions(request):
    query = request.GET.get("q", "").strip()
    results = []
    if len(query) >= 2:
        topics = accessible_topics(request.user).filter(title__icontains=query).select_related("series").order_by("title")[:8]
        results = [
            {"id": topic.pk, "title": topic.title, "series": topic.series.name if topic.series else "Ohne Besprechungsreihe"}
            for topic in topics
        ]
    return JsonResponse({"results": results})


@login_required
@reader_readonly
def agenda_topic_history(request, pk, topic_pk):
    meeting = get_object_or_404(accessible_meetings(request.user), pk=pk)
    item = get_object_or_404(AgendaItem, meeting=meeting, topic_id=topic_pk)
    visible_meetings = accessible_meetings(request.user)
    history = {}
    for entry in AgendaItem.objects.filter(
        topic=item.topic, meeting__in=visible_meetings
    ).select_related("meeting__series", "assigned_to", "topic__assigned_to"):
        history[entry.meeting_id] = {
            "series": entry.meeting.series.name if entry.meeting.series else "Gelöschte Besprechungsreihe",
            "date": entry.meeting.date,
            "text": entry.working_text,
            "responsible": user_display_name(entry.assigned_to or entry.topic.assigned_to) if (entry.assigned_to or entry.topic.assigned_to) else "",
        }
    from .models import TopicSnapshot
    for snapshot in TopicSnapshot.objects.filter(
        topic_id=item.topic_id, meeting__in=visible_meetings
    ).select_related("meeting__series"):
        history[snapshot.meeting_id] = {
            "series": snapshot.meeting.series.name if snapshot.meeting.series else "Gelöschte Besprechungsreihe",
            "date": snapshot.meeting.date,
            "text": snapshot.text,
            "responsible": snapshot.responsible_name,
        }
    # Include a planned follow-up meeting even if its agenda item has not
    # yet been materialized by opening that meeting's agenda.

    entries = sorted(history.values(), key=lambda row: (row["date"], row["series"]), reverse=True)
    return render(request, "meetings/agenda_topic_history.html", {
        "topic": item.topic, "history_entries": entries,
    })

@login_required
@reader_readonly
def topic_edit(request, pk):
    topic = get_object_or_404(accessible_topics(request.user), pk=pk)
    original_topic = Topic.objects.select_related("series", "assigned_to").get(pk=pk)
    writable_series = accessible_series(request.user)
    if not is_admin(request.user):
        writable_series = writable_series.exclude(user_access__role=SeriesAccess.ROLE_READER)
    form = TopicForm(request.POST or None, instance=topic, series_queryset=writable_series, series_required=not is_admin(request.user))
    if is_reader(request.user, topic.series):
        for field in form.fields.values():
            field.disabled = True
    if request.method == "POST" and form.is_valid():
        old_series = original_topic.series
        before = {"title": original_topic.title, "description": original_topic.description,
                  "status": original_topic.status,
                  "series": str(original_topic.series) if original_topic.series else None,
                  "assigned_to": str(original_topic.assigned_to) if original_topic.assigned_to else None}
        updated_topic = form.save(commit=False)
        new_series = updated_topic.series
        after = {"title": updated_topic.title, "description": updated_topic.description,
                 "status": updated_topic.status, "series": str(new_series) if new_series else None,
                 "assigned_to": str(updated_topic.assigned_to) if updated_topic.assigned_to else None}
        labels = {"title": "Titel", "description": "Beschreibung",
                  "status": "Status", "series": "Besprechungsreihe",
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
        "form": form, "topic": topic, "is_reader": is_reader(request.user, topic.series),
        "transfer_series": writable_series.filter(active=True).exclude(pk=topic.series_id),
    })

@login_required
@reader_no_access
def topic_new(request):
    writable_series = accessible_series(request.user)
    if not is_admin(request.user):
        writable_series = writable_series.exclude(user_access__role=SeriesAccess.ROLE_READER)
    form = TopicForm(request.POST or None, series_queryset=writable_series, series_required=not is_admin(request.user))
    if request.method == "POST" and form.is_valid():
        topic = form.save()
        record_event(actor=request.user, action="created", summary=f"Thema „{topic.title}“ angelegt",
                     topic=topic, changes={"Titel": {"vorher": None, "nachher": topic.title}})
        messages.success(request, "Thema angelegt.")
        return redirect("topic_edit", pk=topic.pk)
    return render(request, "meetings/topic_form.html", {"form": form, "is_reader": not has_writable_series(request.user)})

@login_required
@reader_readonly
def topic_archive(request, pk):
    if request.method != "POST":
        return HttpResponseForbidden()
    topic = get_object_or_404(accessible_topics(request.user), pk=pk)
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
@reader_readonly
def topic_reopen(request, pk):
    if request.method != "POST":
        return HttpResponseForbidden()
    topic = get_object_or_404(accessible_topics(request.user), pk=pk, status="archived")
    topic.status = "open"
    topic.save(update_fields=["status", "updated_at"])
    record_event(actor=request.user, action="reopened", summary=f"Thema „{topic.title}“ wieder geöffnet",
                 topic=topic, changes={"Status": {"vorher": "Archiviert", "nachher": "Offen"}})
    messages.success(request, "Thema wurde wieder geöffnet.")
    return redirect("topic_edit", pk=topic.pk)

@login_required
@reader_readonly
def topic_transfer(request, pk):
    if request.method != "POST":
        return HttpResponseForbidden()
    topic = get_object_or_404(accessible_topics(request.user), pk=pk)
    transfer_targets = accessible_series(request.user)
    if not is_admin(request.user):
        transfer_targets = transfer_targets.exclude(user_access__role=SeriesAccess.ROLE_READER)
    target = get_object_or_404(transfer_targets, pk=request.POST.get("series"), active=True)
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
    topics = accessible_topics(request.user).filter(status="archived").select_related("series")
    return render(request, "meetings/archive.html", {"topics": topics})

@login_required
@reader_no_access
def attachment_add(request, pk):
    topic = get_object_or_404(accessible_topics(request.user), pk=pk)
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
                "responsible": snapshot.responsible_name,
            }
            for snapshot in meeting.snapshots.all()
        ]
    return [
        {
            "title": item.topic.title,
            "text": item.working_text,
            "status": item.topic.get_status_display(),
            "responsible": user_display_name(item.assigned_to or item.topic.assigned_to) if (item.assigned_to or item.topic.assigned_to) else "",
        }
        for item in ensure_agenda(meeting)
    ]


def _meeting_participant_names(meeting):
    return [
        user_display_name(user, include_short_description=True)
        for user in meeting.participants.filter(is_active=True).order_by("last_name", "first_name", "username")
    ]


def _meeting_series_name(meeting):
    return meeting.series.name if meeting.series_id else "Gelöschte Besprechungsreihe"


def _protocol_filename(meeting, extension):
    series = slugify(_meeting_series_name(meeting)) or "besprechung"
    return f"protokoll-{series}-{meeting.date:%Y-%m-%d}.{extension}"


@login_required
def protocol_pdf(request, pk):
    meeting = get_object_or_404(accessible_meetings(request.user).select_related("series"), pk=pk)
    entries = _protocol_entries(meeting)

    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, KeepTogether

    organization_name = OrganizationSettings.current_name()
    buffer = BytesIO()
    document = SimpleDocTemplate(
        buffer, pagesize=A4, rightMargin=20 * mm, leftMargin=20 * mm,
        topMargin=20 * mm, bottomMargin=18 * mm,
        title=f"Protokoll – {_meeting_series_name(meeting)}",
        author=f"Meeting Manager – {organization_name}" if organization_name else "Meeting Manager",
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
        Paragraph(escape(_meeting_series_name(meeting)), styles["Heading2"]),
        *([Paragraph(escape(organization_name), styles["Normal"])] if organization_name else []),
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
            *([Paragraph("<b>Verantwortlich:</b> " + escape(entry["responsible"]), styles["Normal"])] if entry.get("responsible") else []),
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
    meeting = get_object_or_404(accessible_meetings(request.user).select_related("series"), pk=pk)
    entries = _protocol_entries(meeting)

    from docx import Document
    from docx.shared import Pt, RGBColor

    organization_name = OrganizationSettings.current_name()
    document = Document()
    document.core_properties.title = f"Protokoll – {_meeting_series_name(meeting)}"
    document.core_properties.author = f"Meeting Manager – {organization_name}" if organization_name else "Meeting Manager"
    document.core_properties.subject = f"Besprechung vom {meeting.date:%d.%m.%Y}"
    document.add_heading("Protokoll", 0)
    document.add_heading(_meeting_series_name(meeting), level=1)
    if organization_name:
        document.add_paragraph(organization_name)
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
        if entry.get("responsible"):
            document.add_paragraph("Verantwortlich: " + entry["responsible"])
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
    meeting = get_object_or_404(accessible_meetings(request.user), pk=pk)
    ensure_agenda(meeting)
    snapshots = meeting.snapshots.all()
    participants = meeting.participants.filter(is_active=True).order_by("last_name", "first_name", "username")
    series_name = meeting.series.name if meeting.series_id else "Gelöschte Besprechungsreihe"
    recipient_emails = []
    if meeting.series_id:
        recipient_emails = list(
            SeriesAccess.objects.filter(
                series_id=meeting.series_id, user__is_active=True
            ).exclude(user__email="").values_list("user__email", flat=True).distinct()
        )
    protocol_url = request.build_absolute_uri(reverse("protocol", args=[meeting.pk]))
    subject = f"Protokoll {series_name} {meeting.date:%d.%m.%Y}"
    body = (
        "Hallo zusammen,\n\n"
        f"das Protokoll für die Sitzung {series_name} am {meeting.date:%d.%m.%Y} "
        f"ist unter {protocol_url} verfügbar.\n"
    )
    mailto_url = (
        f"mailto:{quote(','.join(recipient_emails), safe='@,.-_+')}"
        f"?{urlencode({'subject': subject, 'body': body + '\n'}, quote_via=quote)}"
    )
    return render(request, "meetings/protocol.html", {
        "meeting": meeting, "snapshots": snapshots, "participants": participants,
        "protocol_mailto": mailto_url, "protocol_mail_recipients": recipient_emails,
    })

@login_required
@moderator_required
def series_admin(request):
    today = timezone.localdate()
    series_queryset = accessible_series(request.user)
    if not is_admin(request.user):
        series_queryset = series_queryset.filter(user_access__role=SeriesAccess.ROLE_MODERATOR)
    series = series_queryset.prefetch_related(
        Prefetch(
            "meetings",
            queryset=Meeting.objects.order_by("date", "pk"),
            to_attr="ordered_meetings",
        )
    ).order_by("name")
    for item in series:
        upcoming = next(
            (meeting for meeting in item.ordered_meetings if meeting.date >= today),
            None,
        )
        item.next_meeting = upcoming
        item.other_meetings = [
            meeting for meeting in item.ordered_meetings
            if upcoming is None or meeting.pk != upcoming.pk
        ]
        item.meeting_count = len(item.ordered_meetings)
        item.completed_count = sum(1 for meeting in item.ordered_meetings if meeting.finalized_at)
        item.upcoming_count = sum(1 for meeting in item.ordered_meetings if meeting.date >= today and not meeting.finalized_at)
    expanded_series_id = request.GET.get("expanded", "")
    form = SeriesForm(request.POST or None)
    form.fields.pop("end_date", None)
    if request.method == "POST" and form.is_valid():
        item = form.save(commit=False)
        if not item.end_date:
            item.end_date = date(today.year + 1, 12, 31)
        item.save()
        if not is_admin(request.user):
            SeriesAccess.objects.get_or_create(user=request.user, series=item, defaults={"role": SeriesAccess.ROLE_MODERATOR})
        generate_meetings(item)
        messages.success(request, "Besprechungsreihe und Termine bis zum Serienende angelegt.")
        return redirect("series_admin")
    return render(request, "meetings/series.html", {
        "series": series, "form": form, "today": today,
        "expanded_series_id": expanded_series_id,
    })


@login_required
@moderator_required
def series_edit(request, pk):
    series = get_object_or_404(accessible_series(request.user), pk=pk)
    if not is_moderator(request.user, series):
        return HttpResponseForbidden("Für diese Besprechungsreihe fehlen Moderatorrechte.")
    old_weekday = series.weekday
    form = SeriesForm(request.POST or None, instance=series)
    if request.method == "POST" and form.is_valid():
        weekday_delta = (form.cleaned_data["weekday"] - old_weekday) % 7
        today = timezone.localdate()
        future = list(Meeting.objects.filter(
            series=series, date__gte=today, finalized_at__isnull=True
        ).order_by("date", "pk")) if weekday_delta else []
        target_dates = [meeting.date + timedelta(days=weekday_delta) for meeting in future]
        future_ids = [meeting.pk for meeting in future]
        conflicts = Meeting.objects.filter(series=series, date__in=target_dates).exclude(pk__in=future_ids)
        if conflicts.exists():
            form.add_error("weekday", "Die Verschiebung würde mit einem bereits abgeschlossenen oder anderweitig bestehenden Termin kollidieren.")
        else:
            with transaction.atomic():
                updated = form.save()
                if weekday_delta:
                    for meeting in future:
                        meeting.date = meeting.date + timedelta(days=36500)
                        meeting.save(update_fields=["date"])
                    for meeting in future:
                        meeting.date = meeting.date - timedelta(days=36500 - weekday_delta)
                        meeting.save(update_fields=["date"])
                    if "start_date" not in form.changed_data:
                        updated.start_date = updated.start_date + timedelta(days=weekday_delta)
                        updated.save(update_fields=["start_date"])
                generate_meetings(updated)
            messages.success(request, "Besprechungsreihe gespeichert. Noch nicht abgeschlossene zukünftige Termine wurden auf den neuen Wochentag verschoben.")
            return redirect("series_admin")
    return render(request, "meetings/series_edit.html", {"form": form, "series": series})


@login_required
@moderator_required
def series_extend(request, pk):
    if request.method != "POST":
        return HttpResponseForbidden()
    series = get_object_or_404(accessible_series(request.user), pk=pk)
    if not is_moderator(request.user, series):
        return HttpResponseForbidden("Für diese Besprechungsreihe fehlen Moderatorrechte.")
    today = timezone.localdate()
    target_end = date(today.year + 1, 12, 31)
    if not series.end_date or series.end_date < target_end:
        series.end_date = target_end
        series.save(update_fields=["end_date"])
    created = generate_meetings(series)
    scheduled_count = Meeting.objects.filter(
        series=series, date__gte=today, date__lte=series.end_date
    ).count()
    skipped_count = max(0, scheduled_count - len(created))
    messages.success(
        request,
        f"Die Reihe reicht jetzt bis zum {series.end_date:%d.%m.%Y}. "
        f"{len(created)} neue Termine angelegt; {skipped_count} bereits vorhandene Termine übersprungen."
    )
    return redirect(f"{reverse('series_admin')}?expanded={series.pk}#series-{series.pk}")


@login_required
@moderator_required
def series_reset_meetings(request, pk):
    if request.method != "POST":
        return HttpResponseForbidden()
    series = get_object_or_404(accessible_series(request.user), pk=pk)
    if not is_moderator(request.user, series):
        return HttpResponseForbidden("Für diese Besprechungsreihe fehlen Moderatorrechte.")

    today = timezone.localdate()
    if series.end_date is None:
        series.end_date = date(today.year + 1, 12, 31)
        series.save(update_fields=["end_date"])
    first_possible = max(series.start_date, today)
    next_possible = first_possible + timedelta(days=(series.weekday - first_possible.weekday()) % 7)
    if series.end_date < today or next_possible > series.end_date:
        messages.error(request, "Im gewählten Serienzeitraum kann kein zukünftiger Termin erzeugt werden. Bitte prüfe Start- und Enddatum oder verlängere die Reihe.")
        return redirect("series_edit", pk=series.pk)

    try:
        with transaction.atomic():
            drafts = Meeting.objects.filter(series=series, finalized_at__isnull=True)
            agenda_items = list(
                AgendaItem.objects.filter(meeting__in=drafts)
                .select_related("topic", "meeting")
                .order_by("meeting__date", "pk")
            )
            carried_topics = {}
            for agenda_item in agenda_items:
                carried_topics[agenda_item.topic_id] = (agenda_item.topic, agenda_item.working_text, agenda_item.position, agenda_item.assigned_to_id)
    
            drafts.delete()
            new_meetings = generate_meetings(series)
            next_meeting = (
                Meeting.objects.filter(series=series, finalized_at__isnull=True, date__gte=today)
                .order_by("date", "pk").first()
            )
            if next_meeting is None:
                raise ValueError("Für diese Reihe konnte kein neuer zukünftiger Termin erzeugt werden.")
            for topic, working_text, position, assigned_to_id in carried_topics.values():
                AgendaItem.objects.update_or_create(
                    meeting=next_meeting,
                    topic=topic,
                    defaults={"working_text": working_text, "position": position, "carried_forward": True, "assigned_to_id": assigned_to_id},
                )
    except ValueError as exc:
        messages.error(request, str(exc))
        return redirect("series_edit", pk=series.pk)

    messages.success(
        request,
        f"Alle nicht abgeschlossenen Termine wurden neu erzeugt. "
        f"{len(new_meetings)} Termine angelegt; vorhandene Tagesordnungspunkte "
        f"liegen jetzt auf dem nächsten Termin ({next_meeting.date:%d.%m.%Y}). "
        "Abgeschlossene Termine und Protokolle blieben erhalten."
    )
    return redirect("series_edit", pk=series.pk)


@login_required
@moderator_required
def series_delete(request, pk):
    if request.method != "POST":
        return HttpResponseForbidden()
    series = get_object_or_404(accessible_series(request.user), pk=pk)
    name = series.name
    today = timezone.localdate()
    delete_completed = request.POST.get("delete_completed") == "on"
    with transaction.atomic():
        # Future drafts are removed. Completed meetings are kept by default,
        # together with their immutable protocol snapshots and audit links.
        Meeting.objects.filter(
            series=series, date__gte=today, finalized_at__isnull=True
        ).delete()
        if delete_completed:
            Meeting.objects.filter(series=series, finalized_at__isnull=False).delete()
        # Preserve all remaining historical meetings independently of the series.
        Meeting.objects.filter(series=series).update(series=None)
        series.delete()
    messages.success(
        request,
        f"Die Besprechungsreihe „{name}“ wurde gelöscht. "
        + ("Abgeschlossene Besprechungen wurden ebenfalls entfernt." if delete_completed
           else "Abgeschlossene und sonstige verbleibende Besprechungen samt Protokollen bleiben erhalten.")
    )
    return redirect("series_admin")


@login_required
@moderator_required
def meeting_edit(request, pk):
    meeting = get_object_or_404(accessible_meetings(request.user).select_related("series"), pk=pk)
    if meeting.finalized_at:
        messages.error(request, "Abgeschlossene Besprechungen können nicht verschoben werden.")
        return redirect("meeting", pk=pk)
    form = MeetingDateForm(request.POST or None, instance=meeting)
    if request.method == "POST" and form.is_valid():
        old_date = meeting.date
        updated = form.save(commit=False)
        if accessible_meetings(request.user).filter(series=meeting.series, date=updated.date).exclude(pk=meeting.pk).exists():
            form.add_error("date", "Für diese Besprechungsreihe gibt es an diesem Tag bereits einen Termin.")
        else:
            updated.save()
            if old_date != updated.date:
                record_event(
                    actor=request.user, action="updated",
                    summary=f"Termin von „{_meeting_series_name(meeting)}“ verschoben",
                    meeting=updated,
                    changes={"Datum": {"vorher": old_date.isoformat(), "nachher": updated.date.isoformat()}},
                )
            messages.success(request, "Einzelner Termin wurde verschoben. Der Rhythmus der Reihe bleibt unverändert.")
            return redirect("meeting", pk=updated.pk)
    return render(request, "meetings/meeting_date_form.html", {"form": form, "meeting": meeting})


@login_required
@moderator_required
def meeting_delete(request, pk):
    if request.method != "POST":
        return HttpResponseForbidden()
    meeting = get_object_or_404(accessible_meetings(request.user).select_related("series"), pk=pk)
    if meeting.finalized_at or meeting.snapshots.exists():
        messages.error(request, "Abgeschlossene Besprechungen mit Protokoll können nicht gelöscht werden.")
        return redirect("meeting", pk=pk)
    if not meeting.series_id:
        messages.error(request, "Dieser Termin gehört zu keiner Besprechungsreihe und kann daher nicht verschoben werden.")
        return redirect("meeting", pk=pk)

    with transaction.atomic():
        meeting = Meeting.objects.select_for_update().get(pk=meeting.pk)
        target = (
            Meeting.objects.select_for_update()
            .filter(series=meeting.series, date__gt=meeting.date, finalized_at__isnull=True)
            .order_by("date", "pk")
            .first()
        )
        has_content_to_preserve = meeting.agenda_items.exists() or meeting.participants.exists()
        if has_content_to_preserve and target is None:
            today = timezone.localdate()
            target_end = date(today.year + 1, 12, 31)
            if not meeting.series.end_date or meeting.series.end_date < target_end:
                meeting.series.end_date = target_end
                meeting.series.save(update_fields=["end_date"])
            generate_meetings(meeting.series)
            target = (
                Meeting.objects.select_for_update()
                .filter(series=meeting.series, date__gt=meeting.date, finalized_at__isnull=True)
                .order_by("date", "pk")
                .first()
            )
        if has_content_to_preserve and target is None:
            messages.error(request, "Es konnte kein nachfolgender Termin für die Tagesordnungspunkte angelegt werden. Der Termin bleibt erhalten.")
            return redirect("meeting", pk=pk)

        if target is not None:
            if meeting.participants.exists():
                target.participants.add(*meeting.participants.all())
            next_position = (
                target.agenda_items.order_by("-position").values_list("position", flat=True).first()
                if target.agenda_items.exists() else -1
            ) + 1
            moved_count = 0
            for item in meeting.agenda_items.select_related("topic").order_by("position", "pk"):
                existing = target.agenda_items.filter(topic=item.topic).first()
                if existing:
                    if item.working_text:
                        existing.working_text = "\n".join(
                            part for part in [existing.working_text, item.working_text] if part
                        )
                        existing.save(update_fields=["working_text"])
                    if item.assigned_to_id and not existing.assigned_to_id:
                        existing.assigned_to_id = item.assigned_to_id
                        existing.save(update_fields=["assigned_to"])
                    item.delete()
                else:
                    item.meeting = target
                    item.position = next_position
                    item.carried_forward = True
                    item.save(update_fields=["meeting", "position", "carried_forward"])
                    next_position += 1
                moved_count += 1
        else:
            moved_count = 0
        meeting.delete()

    if moved_count:
        messages.success(request, f"Der Termin wurde gelöscht. {moved_count} Tagesordnungspunkt(e) wurden auf den {target.date:%d.%m.%Y} übertragen.")
    else:
        messages.success(request, "Der einzelne Termin wurde gelöscht. Die Besprechungsreihe bleibt bestehen.")
    return redirect("series_admin")


@login_required
@reader_readonly
def finalize(request, pk):
    if request.method != "POST":
        return HttpResponseForbidden()
    meeting = get_object_or_404(accessible_meetings(request.user), pk=pk)
    if meeting.finalized_at:
        messages.info(request, "Diese Besprechung ist bereits abgeschlossen.")
        return redirect("protocol", pk=pk)
    finalize_meeting(meeting)
    record_event(actor=request.user, action="finalized",
                 summary=f"Besprechung „{_meeting_series_name(meeting)}“ vom {meeting.date:%d.%m.%Y} abgeschlossen",
                 meeting=meeting, changes={"Abgeschlossen": {"vorher": None, "nachher": meeting.finalized_at.isoformat()}})
    messages.success(request, "Besprechung abgeschlossen; Protokoll-Snapshot gespeichert.")
    return redirect("protocol", pk=pk)


@login_required
@moderator_required
def meeting_reopen(request, pk):
    if request.method != "POST":
        return HttpResponseForbidden()
    meeting = get_object_or_404(accessible_meetings(request.user), pk=pk)
    if not meeting.finalized_at:
        messages.info(request, "Diese Besprechung ist bereits geöffnet.")
        return redirect("meeting", pk=pk)

    with transaction.atomic():
        previous_finalized_at = meeting.finalized_at
        previous_snapshot = list(meeting.snapshots.values(
            "topic_title", "text", "status", "topic_id"
        ))
        # Keep the previous immutable protocol in the append-only audit event.
        # Remove active snapshots so a later completion can create a fresh version.
        meeting.snapshots.all().delete()
        meeting.finalized_at = None
        meeting.save(update_fields=["finalized_at"])
        record_event(
            actor=request.user,
            action="reopened",
            summary=f"Besprechung „{_meeting_series_name(meeting)}“ vom {meeting.date:%d.%m.%Y} wieder geöffnet",
            meeting=meeting,
            changes={
                "Abgeschlossen am": {
                    "vorher": previous_finalized_at.isoformat(),
                    "nachher": None,
                },
                "Gesicherter Protokollstand": previous_snapshot,
            },
        )
    messages.success(request, "Besprechung wurde wieder geöffnet. Der vorherige Protokollstand bleibt im Änderungsverlauf erhalten.")
    return redirect("meeting", pk=pk)


@login_required
def audit_history(request):
    admin_access = is_admin(request.user)
    # Änderungsverläufe sind ausschließlich für Serien mit Moderatorrolle sichtbar.
    # Eine Teilnehmerrolle in einer anderen Serie darf die Ansicht nicht erweitern.
    series = (
        MeetingSeries.objects.all()
        if admin_access else
        MeetingSeries.objects.filter(
            user_access__user=request.user,
            user_access__role=SeriesAccess.ROLE_MODERATOR,
        ).distinct()
    )
    has_history_permission = admin_access or series.exists()
    series = series.order_by("name") if has_history_permission else MeetingSeries.objects.none()
    topics = (
        Topic.objects.all() if admin_access else Topic.objects.filter(series__in=series)
    ).order_by("title") if has_history_permission else Topic.objects.none()
    events = AuditEvent.objects.none()
    topic_id = request.GET.get("topic", "")
    selected_series = request.GET.get("series", "")

    if has_history_permission:
        events = AuditEvent.objects.select_related("actor", "topic", "meeting", "meeting__series", "series")
        if not admin_access:
            # Prefer the immutable event context. Legacy rows without it use
            # the former topic-first relation-based fallback.
            events = events.filter(
                Q(series__in=series)
                | (Q(series__isnull=True) & (
                    Q(topic__series__in=series)
                    | (Q(topic__series__isnull=True) & Q(meeting__series__in=series))
                ))
            )
        if selected_series.isdigit() and series.filter(pk=int(selected_series)).exists():
            events = events.filter(
                Q(series_id=int(selected_series))
                | (Q(series__isnull=True) & (
                    Q(topic__series_id=int(selected_series))
                    | Q(meeting__series_id=int(selected_series))
                ))
            )
            topics = topics.filter(series_id=int(selected_series))
        else:
            selected_series = ""
        if topic_id and topics.filter(pk=topic_id).exists():
            events = events.filter(topic_id=topic_id)
        else:
            topic_id = ""
    else:
        topic_id = ""
        selected_series = ""

    return render(request, "meetings/audit_history.html", {
        "events": events[:250], "selected_topic": topic_id,
        "topics": topics, "series": series, "selected_series": selected_series,
        "has_history_permission": has_history_permission,
    })


@login_required
@reader_readonly
def topic_comment_add(request, pk):
    topic = get_object_or_404(accessible_topics(request.user), pk=pk)
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