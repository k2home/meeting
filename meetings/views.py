from datetime import date, datetime, timedelta
from functools import wraps
from io import BytesIO
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from urllib.parse import quote, urlencode
from xml.sax.saxutils import escape

from django.contrib import messages
from django.contrib.auth import login, logout, get_user_model, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.db import transaction
from django.db.models import F, Q, Window, Prefetch, Min, OuterRef, Subquery, Count
from django.db.models.functions import RowNumber
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import formats, timezone
from django.utils.text import slugify
from django.utils.http import url_has_allowed_host_and_scheme
from .forms import PersonalProfileForm, SeriesAccessRequestForm, UsernameLoginForm, TopicCommentForm, AgendaTextForm, AttachmentForm, SeriesForm, MeetingParticipantsForm, MeetingDateForm, AgendaItemCreateForm, AgendaScheduleForm
from .models import Meeting, MeetingSeries, Topic, TopicAttachment, TopicTransferHistory, AuditEvent, AgendaItem, OrganizationSettings, TopicComment, ArchivedMeetingAccess
from .audit import record_event, record_transfer_events
from .services import ensure_agenda, generate_meetings, finalize_meeting
from .access import accessible_meetings, accessible_series, accessible_topics, has_writable_series, is_admin, is_moderator, is_reader
from .models import SeriesAccess, SeriesAccessRequest
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
    if view.__name__ in {"agenda_reorder", "agenda_item_delete", "meeting_detail", "meeting_edit", "meeting_delete", "meeting_reopen", "finalize"}:
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
        archived_meeting = (
            series is None
            and view.__name__ in {"meeting_edit", "meeting_delete", "meeting_reopen"}
            and ArchivedMeetingAccess.objects.filter(
                meeting_id=kwargs.get("pk"), user=request.user
            ).exists()
        )
        allowed = is_admin(request.user) or (
            is_moderator(request.user, series)
            if series is not None else (is_moderator(request.user) and not archived_meeting)
        )
        if not allowed:
            return HttpResponseForbidden("Für diese Besprechungsreihe fehlen Moderatorrechte.")
        return view(request, *args, **kwargs)
    return wrapped


def reader_readonly(view):
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        if request.method == "POST":
            series = _series_for_view(view, kwargs)
            archived_access = False
            if series is None and not is_admin(request.user):
                if view.__name__ in {"agenda_reorder", "agenda_item_delete", "meeting_detail", "finalize"}:
                    archived_access = ArchivedMeetingAccess.objects.filter(
                        meeting_id=kwargs.get("pk"), user=request.user
                    ).exists()
                else:
                    archived_access = ArchivedMeetingAccess.objects.filter(
                        user=request.user, meeting__agenda_items__topic_id=kwargs.get("pk")
                    ).exists()
            if is_reader(request.user, series) or archived_access:
                return HttpResponseForbidden("Für archivierte Besprechungen und Leser*innen besteht ausschließlich Lesezugriff.")
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
    meeting_groups = []
    grouped_meetings = meetings.order_by("series__name", "date", "pk")
    for meeting in grouped_meetings:
        if not meeting_groups or meeting_groups[-1]["series"].pk != meeting.series_id:
            meeting_groups.append({"series": meeting.series, "meetings": []})
        meeting_groups[-1]["meetings"].append(meeting)

    topics = accessible_topics(request.user).exclude(status="archived").select_related("series")
    query = request.GET.get("q", "").strip()
    selected_status = request.GET.get("status", "all" if is_reader(request.user) and not has_writable_series(request.user) else "active")
    selected_series = request.GET.get("series", "")
    selected_assignee = request.GET.get("assigned_to", "" if is_reader(request.user) else str(request.user.pk))
    selected_due = request.GET.get("due", "next_week")

    if selected_status == "active":
        topics = topics.filter(agenda_items__status__in=["open", "in_progress"])
    elif selected_status in {"open", "in_progress", "done"}:
        topics = topics.filter(agenda_items__status=selected_status)
    elif selected_status != "all":
        selected_status = "active"
        topics = topics.filter(agenda_items__status__in=["open", "in_progress"])

    if query:
        topics = topics.filter(
            Q(title__icontains=query)
            | Q(agenda_items__working_text__icontains=query)
            | Q(series__name__icontains=query)
            | Q(agenda_items__assigned_to__username__icontains=query)
            | Q(agenda_items__assigned_to__first_name__icontains=query)
            | Q(agenda_items__assigned_to__last_name__icontains=query)
        )
    if selected_series.isdigit():
        topics = topics.filter(series_id=int(selected_series))
    else:
        selected_series = ""
    if selected_assignee == "unassigned":
        topics = topics.filter(agenda_items__assigned_to__isnull=True)
    elif selected_assignee.isdigit():
        topics = topics.filter(agenda_items__assigned_to_id=int(selected_assignee)).distinct()
    else:
        selected_assignee = ""
    latest_agenda_item = AgendaItem.objects.filter(
        topic_id=OuterRef("pk")
    ).order_by("-meeting__date", "-pk")
    topics = topics.annotate(
        next_meeting_date=Subquery(latest_agenda_item.values("meeting__date")[:1]),
        latest_agenda_status=Subquery(latest_agenda_item.values("status")[:1]),
    )
    if selected_due == "next_week":
        topics = topics.filter(
            next_meeting_date__gte=today,
            next_meeting_date__lte=today + timedelta(days=7),
        )
    elif selected_due == "overdue":
        topics = topics.filter(
            next_meeting_date__lt=today,
            latest_agenda_status__in=["open", "in_progress"],
        )
    elif selected_due == "today":
        topics = topics.filter(next_meeting_date=today)
    elif selected_due == "without_date":
        topics = topics.filter(next_meeting_date__isnull=True)
    elif selected_due == "future":
        topics = topics.filter(next_meeting_date__gt=today)

    topics = topics.distinct()
    overdue_topics = accessible_topics(request.user)
    if not is_admin(request.user):
        overdue_topics = overdue_topics.filter(
            series__user_access__user=request.user,
            series__user_access__role__in=[
                SeriesAccess.ROLE_PARTICIPANT,
                SeriesAccess.ROLE_MODERATOR,
            ],
        )
    overdue_count = (
        overdue_topics.annotate(
            latest_agenda_date=Subquery(latest_agenda_item.values("meeting__date")[:1]),
            latest_agenda_status=Subquery(latest_agenda_item.values("status")[:1]),
        )
        .filter(
            latest_agenda_date__lt=today,
            latest_agenda_status__in=["open", "in_progress"],
        )
        .count()
    )
    return render(request, "meetings/dashboard.html", {
        "meetings": meetings, "meeting_groups": meeting_groups, "topics": topics, "overdue_count": overdue_count, "today": today,
        "query": query, "selected_status": selected_status, "selected_series": selected_series,
        "selected_assignee": selected_assignee, "selected_due": selected_due,
        "series_options": accessible_series(request.user).order_by("name"),
        "own_assignee_label": user_display_name(request.user),
        "assignee_options": sorted(
            UserModel.objects.filter(is_active=True).exclude(pk=request.user.pk),
            key=lambda person: user_display_name(person).casefold(),
        ),
        "new_topic_series": (
            accessible_series(request.user).exclude(user_access__role=SeriesAccess.ROLE_READER)
            if not is_admin(request.user) else accessible_series(request.user)
        ).filter(active=True).distinct().order_by("name"),
        "new_topic_meetings": accessible_meetings(request.user).filter(
            series__in=accessible_series(request.user).filter(active=True),
            date__gte=today, finalized_at__isnull=True,
        ).select_related("series").order_by("series__name", "date"),
        "result_count": topics.count(),
    })


@login_required
def meetings_overview(request):
    """Show only meetings belonging to series the current user may access."""
    today = timezone.localdate()
    series = list(accessible_series(request.user).distinct().order_by("name"))
    meetings = list(
        accessible_meetings(request.user)
        .filter(series__isnull=False)
        .select_related("series")
        .annotate(open_agenda_count=Count(
            "agenda_items",
            filter=Q(agenda_items__status__in=["open", "in_progress"]),
        ))
        .order_by("date", "series__name", "pk")
    )

    role_labels = {
        SeriesAccess.ROLE_PARTICIPANT: "Teilnehmer",
        SeriesAccess.ROLE_READER: "Leser",
        SeriesAccess.ROLE_MODERATOR: "Moderator",
    }
    role_by_series = {}
    if not is_admin(request.user):
        role_by_series = {
            access.series_id: role_labels.get(access.role, access.role)
            for access in SeriesAccess.objects.filter(user=request.user, series__in=series)
        }

    events = []
    for meeting in meetings:
        role = "Administrator" if is_admin(request.user) else role_by_series.get(meeting.series_id, "")
        events.append({
            "id": meeting.pk,
            "date": meeting.date.isoformat(),
            "title": meeting.title or "Besprechung",
            "series": meeting.series.name,
            "role": role,
            "url": reverse("meeting", args=[meeting.pk]),
            "finalized": bool(meeting.finalized_at),
            "open_agenda_count": meeting.open_agenda_count,
        })

    next_by_series = {}
    for meeting in meetings:
        if meeting.date >= today and not meeting.finalized_at:
            next_by_series.setdefault(meeting.series_id, meeting)

    series_rows = []
    for item in series:
        meeting = next_by_series.get(item.pk)
        series_rows.append({
            "series": item,
            "meeting": meeting,
            "role": "Administrator" if is_admin(request.user) else role_by_series.get(item.pk, ""),
            "open_agenda_count": meeting.open_agenda_count if meeting else 0,
        })

    return render(request, "meetings/meetings_overview.html", {
        "today": today,
        "calendar_events": events,
        "calendar_events_json": __import__("json").dumps(events, ensure_ascii=False),
        "series_rows": series_rows,
    })


@login_required
def open_topics(request):
    """Show the latest unfinished agenda entry for topics without a future appointment."""
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

    latest_item_ids = AgendaItem.objects.filter(
        topic_id=OuterRef("topic_id")
    ).order_by("-meeting__date", "-pk").values("pk")[:1]
    items = AgendaItem.objects.filter(
        topic__series__in=allowed_series,
        topic__status__in=["open", "in_progress", "done"],
        status__in=["open", "in_progress"],
        meeting__date__lte=today,
    ).filter(pk__in=Subquery(latest_item_ids)).select_related(
        "topic", "topic__series", "meeting", "assigned_to"
    ).order_by("topic__series__name", "topic__title")

    if request.method == "POST":
        item = get_object_or_404(items, pk=request.POST.get("schedule_item"))
        target_meeting = get_object_or_404(
            Meeting.objects.filter(series=item.topic.series, date__gt=today, finalized_at__isnull=True),
            pk=request.POST.get("target_meeting"),
        )
        with transaction.atomic():
            source_item = item.followup_of or item
            followup = AgendaItem.objects.filter(followup_of=source_item).first()
            next_position = (
                target_meeting.agenda_items.exclude(pk=followup.pk if followup else None)
                .order_by("-position").values_list("position", flat=True).first()
                if target_meeting.agenda_items.exclude(pk=followup.pk if followup else None).exists() else -1
            ) + 1
            if followup:
                followup.meeting = target_meeting
                followup.working_text = ""
                followup.assigned_to_id = source_item.assigned_to_id
                followup.status = source_item.status
                followup.position = next_position
                followup.save(update_fields=["meeting", "working_text", "assigned_to", "status", "position"])
            else:
                AgendaItem.objects.create(
                    meeting=target_meeting, topic=source_item.topic,
                    working_text="",
                    assigned_to_id=source_item.assigned_to_id,
                    status=source_item.status,
                    position=next_position, carried_forward=True, followup_of=source_item,
                )
            record_event(
                actor=request.user, action="updated",
                summary=f"„{item.topic.title}“ auf die Tagesordnung am {formats.date_format(target_meeting.date, 'DATE_FORMAT')} gesetzt",
                topic=item.topic, meeting=target_meeting,
                changes={"Wiedervorlage": {"nachher": target_meeting.date.isoformat()}},
            )
        messages.success(request, f"„{item.topic.title}“ wurde auf die Tagesordnung am {formats.date_format(target_meeting.date, 'DATE_FORMAT')} gesetzt.")
        return redirect("open_topics")

    rows = []
    for item in items:
        future_meetings = Meeting.objects.filter(
            series=item.topic.series, date__gt=today, finalized_at__isnull=True
        ).order_by("date")
        rows.append({"item": item, "future_meetings": future_meetings})
    return render(request, "meetings/open_topics.html", {"rows": rows, "today": today})

@login_required
def my_tasks(request):
    """Separate topic-level ownership from explicit agenda-item assignments."""
    today = timezone.localdate()
    visible_meetings = accessible_meetings(request.user)

    main_topics = list(
        accessible_topics(request.user)
        .filter(assigned_to=request.user, status__in=["open", "in_progress"])
        .select_related("series")
        .annotate(
            next_meeting_date=Min(
                "agenda_items__meeting__date",
                filter=Q(agenda_items__meeting__in=visible_meetings)
                & Q(agenda_items__meeting__finalized_at__isnull=True),
            ),
            latest_agenda_text=Subquery(
                AgendaItem.objects.filter(topic=OuterRef("pk"), meeting__in=visible_meetings)
                .order_by("-meeting__date", "-pk").values("working_text")[:1]
            ),
        )
        .distinct()
        .order_by(F("next_meeting_date").asc(nulls_last=True), "title")
    )

    agenda_tasks = list(
        AgendaItem.objects.filter(
            meeting__in=visible_meetings,
            meeting__date__gte=today,
            meeting__finalized_at__isnull=True,
            assigned_to=request.user,
            status__in=["open", "in_progress"],
        ).select_related("topic", "topic__series", "meeting")
        .order_by("meeting__date", "meeting__series__name", "position", "pk")
    )

    # Keep the historical context key for integrations/tests while rendering
    # the two responsibility types in distinct sections.
    return render(request, "meetings/my_tasks.html", {
        "topics": main_topics,
        "main_topics": main_topics,
        "agenda_tasks": agenda_tasks,
        "today": today,
        "overdue_count": sum(1 for topic in main_topics if topic.next_meeting_date and topic.next_meeting_date < today),
        "due_today_count": sum(1 for topic in main_topics if topic.next_meeting_date == today),
        "without_meeting_count": sum(1 for topic in main_topics if topic.next_meeting_date is None),
    })

@login_required
@reader_readonly
@transaction.atomic
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
    if current_ids != ordered_ids:
        before_titles = [items_by_id[item_id].topic.title for item_id in current_ids]
        after_titles = [items_by_id[item_id].topic.title for item_id in ordered_ids]
        with transaction.atomic():
            AgendaItem.objects.bulk_update(ordered_items, ["position"])
            record_event(
                actor=request.user, action="updated",
                summary=f"Tagesordnung für {_meeting_series_name(meeting)} am {formats.date_format(meeting.date, 'DATE_FORMAT')} sortiert",
                meeting=meeting,
                changes={"Reihenfolge": {"vorher": before_titles, "nachher": after_titles}},
            )
    messages.success(request, "Reihenfolge der Tagesordnung gespeichert.")
    return redirect("meeting", pk=pk)


def _schedule_agenda_followup(item, target_series, target_meeting, actor):
    """Create or move the linked follow-up without partial mutations."""
    with transaction.atomic():
        item = AgendaItem.objects.select_for_update().get(pk=item.pk)
        topic = Topic.objects.select_for_update().get(pk=item.topic_id)
        old_series = topic.series
        followup = AgendaItem.objects.select_for_update().filter(followup_of=item).first()
        conflict = AgendaItem.objects.filter(meeting=target_meeting, topic=topic)
        if followup:
            conflict = conflict.exclude(pk=followup.pk)
        if conflict.exists():
            raise ValueError("Das Thema steht bereits unabhängig auf der gewählten Tagesordnung. Bitte entferne diesen doppelten Eintrag zuerst.")
        if target_meeting.pk == item.meeting_id:
            raise ValueError("Bitte wähle einen anderen, späteren Besprechungstermin.")
        if old_series != target_series and Topic.objects.filter(
            series=target_series, title__iexact=topic.title
        ).exclude(pk=topic.pk).exists():
            raise ValueError("In der Ziel-Besprechungsreihe existiert bereits ein Thema mit diesem Titel. Bitte führe die Themen zuerst zusammen.")
        if old_series != target_series:
            _move_future_agenda_items(topic, old_series, target_series, {item.pk})
        topic.series = target_series
        topic.save(update_fields=["series", "updated_at"])
        remaining = target_meeting.agenda_items.exclude(pk=followup.pk if followup else None)
        next_position = (remaining.order_by("-position").values_list("position", flat=True).first() if remaining.exists() else -1) + 1
        if followup:
            followup.meeting = target_meeting
            followup.working_text = item.working_text
            followup.status = item.status
            followup.assigned_to_id = item.assigned_to_id
            followup.position = next_position
            followup.carried_forward = True
            followup.save(update_fields=["meeting", "working_text", "status", "assigned_to", "position", "carried_forward"])
        else:
            AgendaItem.objects.create(meeting=target_meeting, topic=topic, working_text=item.working_text, assigned_to_id=item.assigned_to_id, status=item.status, position=next_position, carried_forward=True, followup_of=item)
        if old_series != target_series:
            TopicTransferHistory.objects.create(topic=topic, from_series=old_series, to_series=target_series, transferred_by=actor, note=f"Wiedervorlage für {formats.date_format(target_meeting.date, 'DATE_FORMAT')} festgelegt")
        transfer_changes = {"Wiedervorlage": {"nachher": target_meeting.date.isoformat()}}
        transfer_summary = f"Wiedervorlage für „{topic.title}“ auf {target_series.name} am {formats.date_format(target_meeting.date, 'DATE_FORMAT')} gesetzt"
        if old_series != target_series:
            record_transfer_events(
                actor=actor, summary=transfer_summary, topic=topic,
                from_series=old_series, to_series=target_series,
                meeting=item.meeting, changes=transfer_changes,
            )
        else:
            record_event(actor=actor, action="updated", summary=transfer_summary, topic=topic, meeting=item.meeting, changes=transfer_changes)
    return f"„{topic.title}“ steht am {formats.date_format(target_meeting.date, 'DATE_FORMAT')} erneut auf der Tagesordnung von {target_series.name}."


@login_required
@reader_readonly
@transaction.atomic
def agenda_item_delete(request, pk, item_pk):
    if request.method != "POST":
        return HttpResponseForbidden("Diese Aktion ist nur per POST möglich.")
    meeting = get_object_or_404(accessible_meetings(request.user), pk=pk)
    if meeting.finalized_at:
        messages.error(request, "Tagesordnungspunkte abgeschlossener Besprechungen können nicht gelöscht werden.")
        return redirect("meeting", pk=pk)
    item = get_object_or_404(
        AgendaItem.objects.select_for_update().select_related("topic"),
        pk=item_pk, meeting=meeting,
    )
    topic = item.topic
    predecessor_id = item.followup_of_id
    successor = AgendaItem.objects.select_for_update().filter(followup_of=item).first()
    if successor:
        # Release the one-to-one link before reconnecting the successor.
        if predecessor_id:
            item.followup_of = None
            item.save(update_fields=["followup_of"])
            successor.followup_of_id = predecessor_id
        else:
            successor.followup_of = None
        successor.save(update_fields=["followup_of"])
    item.delete()
    record_event(
        actor=request.user, action="updated",
        summary=f"„{topic.title}“ aus der Tagesordnung am {formats.date_format(meeting.date, 'DATE_FORMAT')} entfernt",
        topic=topic, meeting=meeting,
        changes={
            "Tagesordnungspunkt": {"vorher": meeting.date.isoformat(), "nachher": None},
            "Wiedervorlage": {
                "Vorgänger erhalten": bool(predecessor_id and successor),
                "Nachfolger": successor.pk if successor else None,
            },
        },
    )
    messages.success(request, f"„{topic.title}“ wurde aus diesem Besprechungstermin entfernt. Bestehende Wiedervorlagen wurden soweit möglich verbunden; das Thema bleibt bestehen.")
    return redirect("topic_edit", pk=topic.pk)


@login_required
@reader_readonly
@transaction.atomic
def meeting_detail(request, pk):
    meeting = get_object_or_404(accessible_meetings(request.user).select_related("series"), pk=pk)
    archived_readonly = (
        meeting.series_id is None and not is_admin(request.user)
        and ArchivedMeetingAccess.objects.filter(meeting=meeting, user=request.user).exists()
    )
    if not meeting.participants_initialized and not meeting.finalized_at and not archived_readonly:
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
                        summary=f"Teilnehmerliste für „{_meeting_series_name(meeting)}“ am {formats.date_format(meeting.date, 'DATE_FORMAT')} geändert",
                        meeting=meeting,
                        changes={"Teilnehmer": {"vorher": before, "nachher": after}},
                    )
                messages.success(request, "Teilnehmerliste gespeichert.")
            else:
                messages.error(request, "Bitte prüfe die Teilnehmerauswahl.")
                return render(request, "meetings/meeting.html", {
                    "meeting": meeting, "items": items, "participant_form": participant_form,
                    "participants": participants, "assignees": assignees, "is_reader": is_reader(request.user, meeting.series) or archived_readonly,
                    "is_moderator": is_admin(request.user) or (
                        meeting.series_id is not None and is_moderator(request.user, meeting.series)
                    ),
                    "writable_series": writable_series, "target_meetings": target_meetings,
                })
        elif request.POST.get("shift_item"):
            item = get_object_or_404(
                AgendaItem.objects.select_related("topic", "topic__series"),
                pk=request.POST.get("shift_item"), meeting=meeting,
            )
            schedule_form = AgendaScheduleForm(
                request.POST, series_queryset=writable_series, meeting_queryset=target_meetings,
            )
            if schedule_form.is_valid():
                topic = item.topic
                old_series = topic.series
                target_series = schedule_form.cleaned_data["target_series"]
                target_meeting = schedule_form.cleaned_data["target_meeting"]
                try:
                    with transaction.atomic():
                        if target_meeting.pk == meeting.pk:
                            raise ValueError("Bitte wähle einen anderen, späteren Besprechungstermin.")
                        item.working_text = request.POST.get("working_text", item.working_text)
                        item.save(update_fields=["working_text"])
                        if old_series != target_series:
                            _move_future_agenda_items(topic, old_series, target_series, {item.pk})
                        target_item = AgendaItem.objects.filter(meeting=target_meeting, topic=topic).first()
                        if target_item:
                            target_item.working_text = item.working_text
                            target_item.position = (
                                target_meeting.agenda_items.exclude(pk=target_item.pk)
                                .order_by("-position").values_list("position", flat=True).first()
                                if target_meeting.agenda_items.exclude(pk=target_item.pk).exists() else -1
                            ) + 1
                            if item.assigned_to_id and not target_item.assigned_to_id:
                                target_item.assigned_to_id = item.assigned_to_id
                            target_item.save(update_fields=["working_text", "position", "assigned_to"])
                            item.delete()
                        else:
                            next_position = (
                                target_meeting.agenda_items.order_by("-position").values_list("position", flat=True).first()
                                if target_meeting.agenda_items.exists() else -1
                            ) + 1
                            item.meeting = target_meeting
                            item.position = next_position
                            item.save(update_fields=["meeting", "position"])
                        topic.series = target_series
                        topic.save(update_fields=["series", "updated_at"])
                        if old_series != target_series:
                            TopicTransferHistory.objects.create(
                                topic=topic, from_series=old_series, to_series=target_series,
                                transferred_by=request.user,
                                note=f"Agenda-Punkt ohne Besprechung auf {formats.date_format(target_meeting.date, 'DATE_FORMAT')} verschoben",
                            )
                            record_transfer_events(
                                actor=request.user,
                                summary=f"„{topic.title}“ ohne Besprechung von {formats.date_format(meeting.date, 'DATE_FORMAT')} nach {target_series.name} am {formats.date_format(target_meeting.date, 'DATE_FORMAT')} verschoben",
                                topic=topic, from_series=old_series, to_series=target_series,
                                meeting=meeting,
                                changes={
                                    "Tagesordnung": {"vorher": meeting.date.isoformat(), "nachher": target_meeting.date.isoformat()},
                                    "Wiedervorlage": {"nachher": target_meeting.date.isoformat()},
                                    "Besprechungsreihe": {
                                        "vorher": old_series.name if old_series else None,
                                        "nachher": target_series.name,
                                    },
                                },
                            )
                        else:
                            record_event(
                                actor=request.user, action="updated",
                                summary=f"„{topic.title}“ ohne Besprechung auf {target_series.name} am {formats.date_format(target_meeting.date, 'DATE_FORMAT')} verschoben",
                                topic=topic, meeting=meeting,
                                changes={"Tagesordnung": {"vorher": meeting.date.isoformat(), "nachher": target_meeting.date.isoformat()}},
                            )
                except ValueError as exc:
                    messages.error(request, str(exc))
                else:
                    messages.success(request, f"„{topic.title}“ wurde aus dieser Tagesordnung entfernt und auf den {formats.date_format(target_meeting.date, 'DATE_FORMAT')} verschoben.")
            else:
                messages.error(request, "Bitte wähle eine gültige Besprechungsserie und einen dazugehörigen späteren Termin.")
        elif request.POST.get("schedule_item") and not request.POST.get("save_all_working_texts"):
            item = get_object_or_404(AgendaItem.objects.select_related("topic", "topic__series"), pk=request.POST.get("schedule_item"), meeting=meeting)
            schedule_form = AgendaScheduleForm(request.POST, series_queryset=writable_series, meeting_queryset=target_meetings)
            if schedule_form.is_valid():
                item.working_text = request.POST.get("working_text", item.working_text)
                try:
                    with transaction.atomic():
                        item.save(update_fields=["working_text"])
                        success_message = _schedule_agenda_followup(item, schedule_form.cleaned_data["target_series"], schedule_form.cleaned_data["target_meeting"], request.user)
                except ValueError as exc:
                    messages.error(request, str(exc))
                else:
                    messages.success(request, success_message)
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
        elif request.POST.get("update_agenda_status"):
            item = get_object_or_404(AgendaItem, pk=request.POST.get("update_agenda_status"), meeting=meeting)
            new_status = request.POST.get("status")
            valid_statuses = dict(AgendaItem.STATUS)
            if new_status not in valid_statuses:
                messages.error(request, "Bitte wähle einen gültigen Bearbeitungsstand für diesen Tagesordnungspunkt.")
            elif item.status != new_status:
                old_status = item.get_status_display()
                item.status = new_status
                item.save(update_fields=["status"])
                record_event(
                    actor=request.user, action="updated",
                    summary=f"Bearbeitungsstand für Agenda-Punkt „{item.topic.title}“ auf {valid_statuses[new_status]} gesetzt",
                    topic=item.topic, meeting=meeting,
                    changes={"Bearbeitungsstand Tagesordnungspunkt": {"vorher": old_status, "nachher": valid_statuses[new_status]}},
                )
                messages.success(request, "Bearbeitungsstand des Tagesordnungspunkts gespeichert.")
            else:
                messages.info(request, "Der Bearbeitungsstand ist unverändert.")
        elif request.POST.get("add_existing_topic"):
            topic = get_object_or_404(accessible_topics(request.user), pk=request.POST.get("add_existing_topic"))
            if topic.status == "archived":
                messages.error(request, "Archivierte Themen können nicht auf eine Tagesordnung übernommen werden. Öffne das Thema zuerst im Archiv wieder.")
            elif meeting.agenda_items.filter(topic=topic).exists():
                messages.info(request, f"„{topic.title}“ steht bereits auf dieser Tagesordnung.")
            else:
                AgendaItem.objects.create(
                    meeting=meeting, topic=topic, working_text="",
                    position=(meeting.agenda_items.order_by("-position").values_list("position", flat=True).first() if meeting.agenda_items.exists() else -1) + 1,
                )
                record_event(
                    actor=request.user, action="created",
                    summary=f"Vorhandenes Thema „{topic.title}“ in die Tagesordnung am {formats.date_format(meeting.date, 'DATE_FORMAT')} übernommen",
                    topic=topic, meeting=meeting,
                    changes={"Tagesordnung": {"vorher": None, "nachher": meeting.date.isoformat()}},
                )
                messages.success(request, f"„{topic.title}“ wurde in diese Tagesordnung übernommen. Die Hauptverantwortung und Besprechungsreihe des Themas bleiben unverändert.")
        elif request.POST.get("add_agenda_topic"):
            create_form = AgendaItemCreateForm(request.POST)
            if create_form.is_valid():
                title = create_form.cleaned_data["title"].strip()
                working_text = create_form.cleaned_data["working_text"]
                if not title:
                    messages.error(request, "Bitte gib einen Thementitel ein.")
                else:
                    topic = Topic.objects.create(
                        title=title, series=meeting.series,
                    )
                    AgendaItem.objects.create(
                        meeting=meeting, topic=topic, working_text=working_text,
                        assigned_to=create_form.cleaned_data["assigned_to"],
                        position=(meeting.agenda_items.order_by("-position").values_list("position", flat=True).first() if meeting.agenda_items.exists() else -1) + 1,
                    )
                    record_event(
                        actor=request.user, action="created",
                        summary=f"Thema „{topic.title}“ zur Tagesordnung am {formats.date_format(meeting.date, 'DATE_FORMAT')} hinzugefügt",
                        topic=topic, meeting=meeting,
                        changes={"Titel": {"vorher": None, "nachher": topic.title}},
                    )
                    messages.success(request, f"„{topic.title}“ wurde neu angelegt und zur Tagesordnung hinzugefügt.")
            else:
                messages.error(request, "Bitte prüfe den Titel des neuen Themas.")
        elif request.POST.get("save_all_working_texts"):
            changed_count = 0
            followup_failed = False
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
                    summary=f"Agendatext für „{agenda_item.topic.title}“ in {formats.date_format(meeting.date, 'DATE_FORMAT')} geändert",
                    topic=agenda_item.topic, meeting=meeting,
                    changes={"Text": {"vorher": old_text, "nachher": new_text}},
                )
                changed_count += 1
            if request.POST.get("schedule_item"):
                scheduled_item = get_object_or_404(AgendaItem.objects.select_related("topic", "topic__series"), pk=request.POST.get("schedule_item"), meeting=meeting)
                schedule_form = AgendaScheduleForm(request.POST, series_queryset=writable_series, meeting_queryset=target_meetings)
                if schedule_form.is_valid():
                    try:
                        success_message = _schedule_agenda_followup(scheduled_item, schedule_form.cleaned_data["target_series"], schedule_form.cleaned_data["target_meeting"], request.user)
                    except ValueError as exc:
                        followup_failed = True
                        messages.error(request, f"{exc} Die geänderten Tagesordnungstexte wurden unabhängig davon gespeichert; die Wiedervorlage wurde nicht übernommen.")
                    else:
                        messages.success(request, success_message)
                else:
                    followup_failed = True
                    messages.error(request, "Die Wiedervorlage wurde nicht übernommen. Die geänderten Tagesordnungstexte wurden unabhängig davon gespeichert.")
            if changed_count:
                if followup_failed:
                    messages.info(request, f"{changed_count} geänderte Tagesordnungstexte wurden gespeichert; die Wiedervorlage blieb unverändert.")
                else:
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
                    try:
                        with transaction.atomic():
                            saved = form.save()
                            if old_text != saved.working_text:
                                record_event(actor=request.user, action="agenda_edited",
                                    summary=f"Agendatext für „{item.topic.title}“ in {formats.date_format(meeting.date, 'DATE_FORMAT')} geändert",
                                    topic=item.topic, meeting=meeting,
                                    changes={"Text": {"vorher": old_text, "nachher": saved.working_text}})
                            if schedule_form is not None:
                                success_message = _schedule_agenda_followup(
                                    saved,
                                    schedule_form.cleaned_data["target_series"],
                                    schedule_form.cleaned_data["target_meeting"],
                                    request.user,
                                )
                    except ValueError as exc:
                        messages.error(request, f"{exc} Text und Wiedervorlage wurden nicht gespeichert.")
                    else:
                        messages.success(
                            request,
                            "Agendatext und Wiedervorlage gespeichert."
                            if schedule_form is not None else "Agendatext gespeichert.",
                        )
                else:
                    messages.error(request, "Bitte prüfe den Text und die ausgewählte Wiedervorlage.")
        if request.POST.get("item_id") and not request.POST.get("save_all_working_texts"):
            return redirect(reverse("meeting", args=[pk]) + f"#agenda-item-{request.POST.get('item_id')}")
        return redirect("meeting", pk=pk)

    participant_form = MeetingParticipantsForm(instance=meeting)
    return render(request, "meetings/meeting.html", {
        "meeting": meeting, "items": items, "participant_form": participant_form,
        "participants": participants, "assignees": assignees, "is_reader": is_reader(request.user, meeting.series) or archived_readonly,
        "is_moderator": is_admin(request.user) or (
            meeting.series_id is not None and is_moderator(request.user, meeting.series)
        ),
        "writable_series": writable_series, "target_meetings": target_meetings,
    })


@login_required
def topic_suggestions(request):
    query = request.GET.get("q", "").strip()
    results = []
    if len(query) >= 2:
        topics = accessible_topics(request.user).exclude(status="archived").filter(title__icontains=query).select_related("series").order_by("title")[:8]
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
    ).select_related("meeting__series", "assigned_to"):
        history[entry.meeting_id] = {
            "series": _meeting_series_name(entry.meeting),
            "date": entry.meeting.date,
            "text": entry.working_text,
            "responsible": user_display_name(entry.assigned_to) if entry.assigned_to else "",
        }
    from .models import TopicSnapshot
    for snapshot in TopicSnapshot.objects.filter(
        topic_id=item.topic_id, meeting__in=visible_meetings
    ).select_related("meeting__series"):
        history[snapshot.meeting_id] = {
            "series": _meeting_series_name(snapshot.meeting),
            "date": snapshot.meeting.date,
            "text": snapshot.text,
            "responsible": snapshot.responsible_name,
                "followup_date": snapshot.followup_date,
        }
    # Include a planned follow-up meeting even if its agenda item has not
    # yet been materialized by opening that meeting's agenda.

    entries = sorted(history.values(), key=lambda row: (row["date"], row["series"]), reverse=True)
    return render(request, "meetings/agenda_topic_history.html", {
        "topic": item.topic, "history_entries": entries,
    })

@transaction.atomic
def _move_future_agenda_items(topic, from_series, to_series, exclude_item_ids=None):
    """Move future entries while retaining predecessor and successor links."""
    if from_series == to_series:
        return 0
    today = timezone.localdate()
    source_items = list(AgendaItem.objects.filter(
        topic=topic, meeting__series=from_series, meeting__date__gte=today,
        meeting__finalized_at__isnull=True,
    ).exclude(pk__in=exclude_item_ids or []).select_related("meeting", "followup_of").order_by("meeting__date", "position", "pk"))
    moved = 0
    for item in source_items:
        target_meeting = Meeting.objects.filter(series=to_series, date__gte=item.meeting.date, finalized_at__isnull=True).order_by("date", "pk").first()
        if target_meeting is None and to_series is not None:
            extension_end = date(max(today.year + 1, item.meeting.date.year + 1), 12, 31)
            if not to_series.end_date or to_series.end_date < extension_end:
                to_series.end_date = extension_end
                to_series.save(update_fields=["end_date"])
            generate_meetings(to_series)
            target_meeting = Meeting.objects.filter(series=to_series, date__gte=item.meeting.date, finalized_at__isnull=True).order_by("date", "pk").first()
        if target_meeting is None and to_series is None:
            target_meeting = Meeting.objects.create(series=None, date=item.meeting.date, title="")
        if target_meeting is None:
            target_name = to_series.name if to_series else "Ohne Besprechungsreihe"
            raise ValueError(f"Für „{target_name}“ konnte kein zukünftiger Besprechungstermin gefunden werden.")
        target_item = target_meeting.agenda_items.filter(topic=topic).first()
        if target_item:
            source_parent = item.followup_of
            source_child = AgendaItem.objects.filter(followup_of=item).first()
            target_parent = target_item.followup_of
            target_child = AgendaItem.objects.filter(followup_of=target_item).first()
            if source_parent and target_parent and source_parent.pk != target_parent.pk:
                raise ValueError("Zusammenführung abgebrochen: unterschiedliche Wiedervorlage-Vorgänger.")
            if source_child and target_child and source_child.pk != target_child.pk:
                raise ValueError("Zusammenführung abgebrochen: unterschiedliche Wiedervorlage-Nachfolger.")
            target_item.working_text = "\n".join(x for x in [target_item.working_text, item.working_text] if x)
            if item.assigned_to_id and not target_item.assigned_to_id:
                target_item.assigned_to_id = item.assigned_to_id
            target_item.status = item.status
            if source_parent and not target_parent:
                item.followup_of = None
                item.save(update_fields=["followup_of"])
                target_item.followup_of = source_parent
            if source_child and not target_child:
                source_child.followup_of = target_item
                source_child.save(update_fields=["followup_of"])
            target_item.save(update_fields=["working_text", "assigned_to", "status", "followup_of"])
            item.delete()
        else:
            next_position = (target_meeting.agenda_items.order_by("-position").values_list("position", flat=True).first() if target_meeting.agenda_items.exists() else -1) + 1
            item.meeting = target_meeting
            item.position = next_position
            item.save(update_fields=["meeting", "position"])
        moved += 1
    return moved


@login_required
@reader_readonly
@transaction.atomic
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
    moved_agenda_items = 0
    old_series = topic.series
    try:
        with transaction.atomic():
            moved_agenda_items = _move_future_agenda_items(topic, old_series, target)
            TopicTransferHistory.objects.create(
                topic=topic, from_series=old_series, to_series=target,
                transferred_by=request.user, note=note,
            )
            old_series_name = str(topic.series) if topic.series else "Ohne Reihe"
            topic.series = target
            topic.save(update_fields=["series", "updated_at"])
            record_transfer_events(
                actor=request.user,
                summary=f"Thema „{topic.title}“ nach „{target.name}“ übertragen",
                topic=topic, from_series=old_series,
                to_series=target,
                changes={"Besprechungsreihe": {"vorher": old_series_name, "nachher": target.name},
                         "Geplante Tagesordnungspunkte": {"übertragen": moved_agenda_items},
                         "Notiz": note},
            )
    except ValueError as exc:
        messages.error(request, str(exc))
        return redirect("topic_edit", pk=topic.pk)
    messages.success(request, f"Thema wurde nach „{target.name}“ übertragen. {moved_agenda_items} zukünftige Tagesordnungspunkte wurden übernommen. Die bisherige Zuordnung bleibt in der Historie erhalten.")
    return redirect("topic_edit", pk=topic.pk)

@login_required
def archive(request):
    items = AgendaItem.objects.filter(
        meeting__in=accessible_meetings(request.user), status="done"
    ).select_related("topic", "meeting", "meeting__series", "assigned_to").order_by(
        "-meeting__date", "topic__title", "position"
    )
    archived_topics = accessible_topics(request.user).filter(status="archived").select_related("series").order_by("title")
    return render(request, "meetings/archive.html", {"items": items, "archived_topics": archived_topics})

@login_required
@reader_no_access
@transaction.atomic
def attachment_add(request, pk):
    topic = get_object_or_404(accessible_topics(request.user), pk=pk)
    if topic.series_id is None and not is_admin(request.user):
        return HttpResponseForbidden("Archivierte Themen sind schreibgeschützt.")
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
def attachment_download(request, pk):
    attachment = get_object_or_404(
        TopicAttachment.objects.select_related("topic__series"),
        pk=pk, topic__in=accessible_topics(request.user),
    )
    from .secure_files import serve_topic_upload
    return serve_topic_upload(attachment)


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
            "status": item.get_status_display(),
            "responsible": user_display_name(item.assigned_to) if item.assigned_to else "",
            "followup_date": item.followup_item.meeting.date if hasattr(item, "followup_item") else None,
        }
        for item in ensure_agenda(meeting)
    ]


def _meeting_participant_names(meeting):
    return [
        user_display_name(user, include_short_description=True)
        for user in meeting.participants.filter(is_active=True).order_by("last_name", "first_name", "username")
    ]


def _meeting_series_name(meeting):
    if meeting.series_id:
        return meeting.series.name
    return meeting.archived_series_name or "Gelöschte Besprechungsreihe"


def _protocol_filename(meeting, extension):
    series = slugify(_meeting_series_name(meeting)) or "besprechung"
    return f"protokoll-{series}-{meeting.date:%Y-%m-%d}.{extension}"


@login_required
def protocol_pdf(request, pk):
    meeting = get_object_or_404(accessible_meetings(request.user).select_related("series"), pk=pk)
    entries = _protocol_entries(meeting)

    from reportlab.lib import colors
    from reportlab.lib.enums import TA_LEFT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, KeepTogether, Table, TableStyle, HRFlowable

    organization_name = OrganizationSettings.current_name()
    brand = OrganizationSettings.current_brand_colors()

    def brand_color(value, fallback):
        try:
            return colors.HexColor(value)
        except (TypeError, ValueError):
            return colors.HexColor(fallback)

    primary = brand_color(brand.get("primary_color"), "#00549F")
    secondary = brand_color(brand.get("secondary_color"), "#8FC5FF")
    tertiary = brand_color(brand.get("tertiary_color"), "#FFCC00")

    def readable_text(background):
        luminance = 0.2126 * background.red + 0.7152 * background.green + 0.0722 * background.blue
        return colors.white if luminance < 0.52 else colors.HexColor("#17212B")

    primary_text, secondary_text = readable_text(primary), readable_text(secondary)
    buffer = BytesIO()
    left_margin = right_margin = 20 * mm
    document = SimpleDocTemplate(
        buffer, pagesize=A4, rightMargin=right_margin, leftMargin=left_margin,
        topMargin=25 * mm, bottomMargin=20 * mm,
        title=f"Protokoll – {_meeting_series_name(meeting)}",
        author=f"Meeting Manager – {organization_name}" if organization_name else "Meeting Manager",
        subject=f"Besprechung vom {formats.date_format(meeting.date, 'DATE_FORMAT')}",
    )

    regular_font, bold_font = "Helvetica", "Helvetica-Bold"
    font_path = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
    bold_path = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
    if font_path.exists() and bold_path.exists():
        if "MeetingDejaVu" not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont("MeetingDejaVu", str(font_path)))
            pdfmetrics.registerFont(TTFont("MeetingDejaVu-Bold", str(bold_path)))
        regular_font, bold_font = "MeetingDejaVu", "MeetingDejaVu-Bold"

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="ProtocolHero", parent=styles["Title"], fontName=bold_font,
        fontSize=23, leading=29, alignment=TA_LEFT, textColor=primary_text, spaceAfter=2 * mm,
    ))
    styles.add(ParagraphStyle(
        name="ProtocolSeries", parent=styles["Normal"], fontName=regular_font,
        fontSize=11, leading=16, textColor=primary_text,
    ))
    styles.add(ParagraphStyle(
        name="ProtocolSection", parent=styles["Heading2"], fontName=bold_font,
        fontSize=13, leading=17, textColor=primary, spaceBefore=6 * mm,
        spaceAfter=2.5 * mm, keepWithNext=True,
    ))
    styles.add(ParagraphStyle(
        name="ProtocolTopic", parent=styles["Heading2"], fontName=bold_font,
        fontSize=12, leading=16, textColor=primary, spaceBefore=5 * mm,
        spaceAfter=2 * mm, keepWithNext=True,
    ))
    styles.add(ParagraphStyle(
        name="ProtocolBody", parent=styles["BodyText"], fontName=regular_font,
        fontSize=9.5, leading=15, textColor=colors.HexColor("#263445"),
        spaceAfter=2 * mm, splitLongWords=True,
    ))
    styles.add(ParagraphStyle(
        name="ProtocolMeta", parent=styles["Normal"], fontName=regular_font,
        fontSize=8.5, leading=12, textColor=colors.HexColor("#526170"),
    ))
    styles.add(ParagraphStyle(
        name="ProtocolStatus", parent=styles["Normal"], fontName=bold_font,
        fontSize=8, leading=11, textColor=primary,
    ))
    styles.add(ParagraphStyle(
        name="ProtocolSmall", parent=styles["Normal"], fontName=regular_font,
        fontSize=8.5, leading=12, textColor=colors.HexColor("#526170"),
    ))

    page_width = A4[0] - left_margin - right_margin
    hero = Table([[
        Paragraph("PROTOKOLL", styles["ProtocolHero"]),
        Paragraph(escape(_meeting_series_name(meeting)), styles["ProtocolSeries"]),
    ]], colWidths=[page_width * 0.36, page_width * 0.64])
    hero.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), primary),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7 * mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7 * mm),
        ("TOPPADDING", (0, 0), (-1, -1), 7 * mm),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7 * mm),
    ]))
    state_label = (
        f"Gesicherter Stand · {formats.date_format(timezone.localtime(meeting.finalized_at), 'DATETIME_FORMAT')}"
        if meeting.finalized_at else "Entwurf – nicht abgeschlossen"
    )
    metadata = [
        [Paragraph("<b>Datum</b>", styles["ProtocolMeta"]),
         Paragraph(escape(formats.date_format(meeting.date, "DATE_FORMAT")), styles["ProtocolBody"])],
        [Paragraph("<b>Status</b>", styles["ProtocolMeta"]),
         Paragraph(escape(state_label), styles["ProtocolBody"])],
    ]
    if organization_name:
        metadata.append([
            Paragraph("<b>Organisation</b>", styles["ProtocolMeta"]),
            Paragraph(escape(organization_name), styles["ProtocolBody"]),
        ])
    meta_table = Table(metadata, colWidths=[30 * mm, page_width - 30 * mm])
    meta_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F3F6F9")),
        ("BACKGROUND", (0, 0), (0, -1), secondary),
        ("TEXTCOLOR", (0, 0), (0, -1), secondary_text),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4 * mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4 * mm),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5 * mm),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1 * mm),
        ("LINEBELOW", (0, 0), (-1, -1), 0.4, colors.HexColor("#DCE3EA")),
    ]))

    story = [
        hero, Spacer(1, 5 * mm), meta_table, Spacer(1, 4 * mm),
        HRFlowable(width="100%", thickness=2, color=tertiary, spaceBefore=1 * mm, spaceAfter=2 * mm),
    ]
    participants = _meeting_participant_names(meeting)
    story.append(Paragraph("Teilnehmer", styles["ProtocolSection"]))
    story.append(Paragraph(
        " · ".join(escape(name) for name in participants) if participants else "Keine Teilnehmer eingetragen.",
        styles["ProtocolBody"] if participants else styles["ProtocolSmall"],
    ))
    story.append(Paragraph("Tagesordnung und Ergebnisse", styles["ProtocolSection"]))
    for index, entry in enumerate(entries, start=1):
        parts = [Paragraph(f"{index:02d} &nbsp; {escape(entry['title'])}", styles["ProtocolTopic"])]
        if entry.get("responsible"):
            parts.append(Paragraph("<b>Verantwortlich:</b> " + escape(entry["responsible"]), styles["ProtocolSmall"]))
        if entry.get("followup_date"):
            followup_label = formats.date_format(entry["followup_date"], "DATE_FORMAT")
            parts.append(Paragraph("<b>Wiedervorlage:</b> " + escape(followup_label), styles["ProtocolSmall"]))
        parts.append(Paragraph(escape(entry["text"] or "—").replace("\n", "<br/>"), styles["ProtocolBody"]))
        parts.append(Paragraph("STATUS&nbsp;&nbsp; " + escape(entry["status"]), styles["ProtocolStatus"]))
        parts.append(Spacer(1, 2 * mm))
        story.append(KeepTogether(parts))
    if not entries:
        story.append(Paragraph("Keine Tagesordnungspunkte vorhanden.", styles["ProtocolSmall"]))

    def draw_page(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(primary)
        canvas.rect(0, A4[1] - 3 * mm, A4[0], 3 * mm, fill=1, stroke=0)
        canvas.setStrokeColor(colors.HexColor("#DCE3EA"))
        canvas.setLineWidth(0.5)
        canvas.line(left_margin, 15 * mm, A4[0] - right_margin, 15 * mm)
        canvas.setFont(regular_font, 7.5)
        canvas.setFillColor(colors.HexColor("#687684"))
        canvas.drawString(left_margin, 10.5 * mm, _meeting_series_name(meeting)[:90])
        canvas.drawRightString(A4[0] - right_margin, 10.5 * mm, f"Seite {doc.page}")
        canvas.restoreState()

    document.build(story, onFirstPage=draw_page, onLaterPages=draw_page)
    response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{_protocol_filename(meeting, "pdf")}"'
    return response


@login_required
def protocol(request, pk):
    meeting = get_object_or_404(accessible_meetings(request.user), pk=pk)
    ensure_agenda(meeting)
    snapshots = meeting.snapshots.all()
    participants = meeting.participants.filter(is_active=True).order_by("last_name", "first_name", "username")
    series_name = _meeting_series_name(meeting)
    recipient_emails = []
    if meeting.series_id:
        recipient_emails = list(
            SeriesAccess.objects.filter(
                series_id=meeting.series_id, user__is_active=True
            ).exclude(user__email="").values_list("user__email", flat=True).distinct()
        )
    protocol_url = request.build_absolute_uri(reverse("protocol", args=[meeting.pk]))
    subject = f"Protokoll {series_name} {formats.date_format(meeting.date, 'DATE_FORMAT')}"
    body = (
        "Hallo zusammen,\n\n"
        f"das Protokoll für die Sitzung {series_name} am {formats.date_format(meeting.date, 'DATE_FORMAT')} "
        f"ist unter {protocol_url} verfügbar.\n"
    )
    mailto_query = urlencode(
        {"subject": subject, "body": body + "\n"},
        quote_via=quote,
    )
    mailto_url = (
        f"mailto:{quote(','.join(recipient_emails), safe='@,.-_+')}"
        f"?{mailto_query}"
    )
    return render(request, "meetings/protocol.html", {
        "meeting": meeting, "snapshots": snapshots, "participants": participants,
        "protocol_mailto": mailto_url, "protocol_mail_recipients": recipient_emails,
        "can_reopen_meeting": is_admin(request.user) or (
            meeting.series_id is not None and is_moderator(request.user, meeting.series)
        ),
    })

@login_required
@moderator_required
def series_admin(request):
    today = timezone.localdate()
    if request.method == "POST" and request.POST.get("form_type") == "access_request_decision":
        request_id = request.POST.get("request_id")
        access_request = get_object_or_404(SeriesAccessRequest.objects.select_related("series"), pk=request_id, status=SeriesAccessRequest.STATUS_PENDING)
        if not is_admin(request.user) and not is_moderator(request.user, access_request.series):
            return HttpResponseForbidden("Du darfst Anträge nur für Besprechungsreihen bearbeiten, in denen du Moderator bist.")
        decision = request.POST.get("decision")
        if decision not in {SeriesAccessRequest.STATUS_APPROVED, SeriesAccessRequest.STATUS_REJECTED}:
            return HttpResponseForbidden("Ungültige Entscheidung.")
        with transaction.atomic():
            access_request = SeriesAccessRequest.objects.select_for_update().get(pk=access_request.pk, status=SeriesAccessRequest.STATUS_PENDING)
            if decision == SeriesAccessRequest.STATUS_APPROVED:
                role_rank = {
                    SeriesAccess.ROLE_NONE: -1,
                    SeriesAccess.ROLE_READER: 0,
                    SeriesAccess.ROLE_PARTICIPANT: 1,
                    SeriesAccess.ROLE_MODERATOR: 2,
                }
                current_access = SeriesAccess.objects.filter(
                    user=access_request.user, series=access_request.series
                ).first()
                if access_request.requested_role == SeriesAccess.ROLE_NONE:
                    if current_access:
                        current_access.delete()
                elif current_access is None or role_rank[access_request.requested_role] > role_rank[current_access.role]:
                    SeriesAccess.objects.update_or_create(
                        user=access_request.user, series=access_request.series,
                        defaults={"role": access_request.requested_role},
                    )
            access_request.status = decision
            access_request.decision_note = request.POST.get("decision_note", "").strip()[:500]
            access_request.decided_by = request.user
            access_request.decided_at = timezone.now()
            access_request.save(update_fields=["status", "decision_note", "decided_by", "decided_at"])
        messages.success(request, "Der Berechtigungsantrag wurde bearbeitet.")
        return redirect("series_admin")
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
        with transaction.atomic():
            item.save()
            if not is_admin(request.user):
                SeriesAccess.objects.get_or_create(user=request.user, series=item, defaults={"role": SeriesAccess.ROLE_MODERATOR})
            created_meetings = generate_meetings(item)
            record_event(
                actor=request.user, action="created",
                summary=f"Besprechungsreihe „{item.name}“ angelegt",
                series=item,
                changes={
                    "Bezeichnung": {"vorher": None, "nachher": item.name},
                    "Wiederholung": {"vorher": None, "nachher": item.recurrence},
                    "Intervall": {"vorher": None, "nachher": item.recurrence_interval},
                    "Wochentag": {"vorher": None, "nachher": item.weekday},
                    "Startdatum": {"vorher": None, "nachher": item.start_date.isoformat()},
                    "Enddatum": {"vorher": None, "nachher": item.end_date.isoformat() if item.end_date else None},
                    "Angelegte Termine": len(created_meetings),
                },
            )
        messages.success(request, "Besprechungsreihe und Termine bis zum Serienende angelegt.")
        return redirect("series_admin")
    pending_requests = SeriesAccessRequest.objects.filter(
        status=SeriesAccessRequest.STATUS_PENDING
    ).select_related("user", "series").order_by("created_at")
    if not is_admin(request.user):
        pending_requests = pending_requests.filter(
            series__user_access__user=request.user,
            series__user_access__role=SeriesAccess.ROLE_MODERATOR,
        ).distinct()
    return render(request, "meetings/series.html", {
        "series": series, "form": form, "today": today,
        "expanded_series_id": expanded_series_id,
        "pending_access_requests": pending_requests,
    })


@login_required
@moderator_required
def series_edit(request, pk):
    series = get_object_or_404(accessible_series(request.user), pk=pk)
    if not is_moderator(request.user, series):
        return HttpResponseForbidden("Für diese Besprechungsreihe fehlen Moderatorrechte.")
    old_weekday = series.weekday
    original_values = {
        "name": series.name,
        "description": series.description,
        "recurrence": series.recurrence,
        "recurrence_interval": series.recurrence_interval,
        "weekday": series.weekday,
        "start_date": series.start_date.isoformat(),
        "end_date": series.end_date.isoformat() if series.end_date else None,
    }
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
            try:
                with transaction.atomic():
                    before = original_values
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
                    created_meetings = generate_meetings(updated)
                    after = {
                        "name": updated.name,
                        "description": updated.description,
                        "recurrence": updated.recurrence,
                        "recurrence_interval": updated.recurrence_interval,
                        "weekday": updated.weekday,
                        "start_date": updated.start_date.isoformat(),
                        "end_date": updated.end_date.isoformat() if updated.end_date else None,
                    }
                    labels = {
                        "name": "Bezeichnung", "description": "Beschreibung",
                        "recurrence": "Wiederholung", "recurrence_interval": "Intervall",
                        "weekday": "Wochentag", "start_date": "Startdatum", "end_date": "Enddatum",
                    }
                    changes = {
                        label: {"vorher": before[field], "nachher": after[field]}
                        for field, label in labels.items() if before[field] != after[field]
                    }
                    if changes:
                        changes["Neu angelegte Termine"] = len(created_meetings)
                        record_event(
                            actor=request.user, action="updated",
                            summary=f"Besprechungsreihe „{updated.name}“ geändert",
                            series=updated, changes=changes,
                        )
            except ValueError as exc:
                form.add_error(None, str(exc))
            else:
                messages.success(request, "Besprechungsreihe gespeichert. Tagesordnungspunkte aus entfallenden zukünftigen Terminen wurden dem zeitlich nächstgelegenen neuen Termin zugeordnet; abgeschlossene Protokolle blieben unverändert.")
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
    previous_end = series.end_date
    today = timezone.localdate()
    target_end = date(today.year + 1, 12, 31)
    with transaction.atomic():
        if not series.end_date or series.end_date < target_end:
            series.end_date = target_end
            series.save(update_fields=["end_date"])
        created = generate_meetings(series)
        scheduled_count = Meeting.objects.filter(
            series=series, date__gte=today, date__lte=series.end_date
        ).count()
        skipped_count = max(0, scheduled_count - len(created))
        record_event(
            actor=request.user, action="series_extended",
            summary=f"Besprechungsreihe „{series.name}“ bis zum {formats.date_format(series.end_date, 'DATE_FORMAT')} verlängert",
            series=series,
            changes={
                "Enddatum": {
                    "vorher": previous_end.isoformat() if previous_end else None,
                    "nachher": series.end_date.isoformat(),
                },
                "Neue Termine": len(created),
                "Vorhandene Termine": skipped_count,
            },
        )
    messages.success(
        request,
        f"Die Reihe reicht jetzt bis zum {formats.date_format(series.end_date, 'DATE_FORMAT')}. "
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
    effective_end_date = series.end_date or date(today.year + 1, 12, 31)
    first_possible = max(series.start_date, today)
    next_possible = first_possible + timedelta(days=(series.weekday - first_possible.weekday()) % 7)
    if effective_end_date < today or next_possible > effective_end_date:
        messages.error(request, "Im gewählten Serienzeitraum kann kein zukünftiger Termin erzeugt werden. Bitte prüfe Start- und Enddatum oder verlängere die Reihe.")
        return redirect("series_edit", pk=series.pk)

    try:
        with transaction.atomic():
            if series.end_date is None:
                series.end_date = effective_end_date
                series.save(update_fields=["end_date"])
            drafts = Meeting.objects.filter(series=series, finalized_at__isnull=True, date__gte=today)
            payload = []
            draft_item_ids = set(AgendaItem.objects.filter(meeting__in=drafts).values_list("pk", flat=True))
            for old_meeting in drafts.prefetch_related("participants"):
                participants = list(old_meeting.participants.all())
                for item in old_meeting.agenda_items.select_related("topic", "followup_of").order_by("position", "pk"):
                    payload.append({
                        "old_date": old_meeting.date, "topic": item.topic,
                        "working_text": item.working_text, "position": item.position,
                        "assigned_to_id": item.assigned_to_id, "status": item.status,
                        "old_id": item.pk, "followup_of_id": item.followup_of_id,
                    })
                old_meeting._reset_participants = participants

            participant_payload = [(m.date, list(m.participants.all())) for m in drafts.prefetch_related("participants")]
            drafts.delete()
            created = generate_meetings(series)
            targets = list(Meeting.objects.filter(
                series=series, date__gte=today, finalized_at__isnull=True
            ).order_by("date", "pk"))
            if not targets:
                raise ValueError("Für diese Reihe konnte kein neuer zukünftiger Termin erzeugt werden.")

            for old_date, participants in participant_payload:
                target = min(targets, key=lambda m: (abs((m.date - old_date).days), m.date))
                if participants:
                    target.participants.add(*participants)

            status_rank = {"open": 0, "in_progress": 1, "done": 2}
            restored_items = {}
            for saved in payload:
                nearest_targets = sorted(
                    targets, key=lambda m: (abs((m.date - saved["old_date"]).days), m.date)
                )
                target = next(
                    (candidate for candidate in nearest_targets
                     if not candidate.agenda_items.filter(topic=saved["topic"]).exists()),
                    nearest_targets[0],
                )
                existing = target.agenda_items.filter(topic=saved["topic"]).first()
                if existing:
                    existing.working_text = "\n\n".join(dict.fromkeys(
                        text for text in (existing.working_text, saved["working_text"]) if text
                    ))
                    if not existing.assigned_to_id and saved["assigned_to_id"]:
                        existing.assigned_to_id = saved["assigned_to_id"]
                    elif existing.assigned_to_id and saved["assigned_to_id"] and existing.assigned_to_id != saved["assigned_to_id"]:
                        TopicComment.objects.create(
                            topic=saved["topic"], author=None,
                            body=f"Beim Zurücksetzen der Besprechungsreihe wurden zwei Tagesordnungspunkte zusammengeführt. Die aktive Punktzuständigkeit bleibt bestehen; zusätzlich war {user_display_name(UserModel.objects.get(pk=saved['assigned_to_id']))} für den zusammengeführten Punkt eingetragen.",
                        )
                    if status_rank.get(saved["status"], 0) > status_rank.get(existing.status, 0):
                        existing.status = saved["status"]
                    existing.carried_forward = True
                    existing.save(update_fields=["working_text", "assigned_to", "status", "carried_forward"])
                    restored_items[saved["old_id"]] = existing
                else:
                    next_position = (target.agenda_items.order_by("-position").values_list("position", flat=True).first() if target.agenda_items.exists() else -1) + 1
                    restored_items[saved["old_id"]] = AgendaItem.objects.create(
                        meeting=target, topic=saved["topic"], working_text=saved["working_text"],
                        position=max(next_position, saved["position"]),
                        assigned_to_id=saved["assigned_to_id"], status=saved["status"],
                        carried_forward=True,
                    )
            for saved in payload:
                predecessor_id = saved["followup_of_id"]
                if not predecessor_id:
                    continue
                restored = restored_items[saved["old_id"]]
                predecessor = restored_items.get(predecessor_id) or AgendaItem.objects.filter(pk=predecessor_id).first()
                if predecessor is None:
                    raise ValueError("Eine Wiedervorlage konnte beim Zurücksetzen nicht mehr zugeordnet werden.")
                if restored.followup_of_id and restored.followup_of_id != predecessor.pk:
                    raise ValueError("Eine Wiedervorlage kollidiert beim Zurücksetzen mit einer bestehenden Verknüpfung.")
                if AgendaItem.objects.filter(followup_of=predecessor).exclude(pk=restored.pk).exists():
                    raise ValueError("Ein Wiedervorlage-Vorgänger hätte nach dem Zurücksetzen mehrere Nachfolger.")
                restored.followup_of = predecessor
                restored.save(update_fields=["followup_of"])
            record_event(
                actor=request.user, action="series_reset",
                summary=f"Zukünftige Entwurfstermine der Besprechungsreihe „{series.name}“ neu aufgesetzt",
                series=series,
                changes={
                    "Neu angelegte Termine": len(created),
                    "Übertragene Tagesordnungspunkte": len(payload),
                },
            )
    except ValueError as exc:
        messages.error(request, str(exc))
        return redirect("series_edit", pk=series.pk)

    messages.success(
        request,
        f"Alle zukünftigen Entwurfstermine wurden neu erzeugt. {len(created)} Termine neu angelegt; "
        "Tagesordnungspunkte und Teilnehmende wurden jeweils dem zeitlich nächstgelegenen neuen Termin zugeordnet. "
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
        # Preserve former series members' read access to retained protocols.
        former_access = list(
            SeriesAccess.objects.filter(series=series).values("user_id", "role")
        )
        remaining_meeting_ids = list(Meeting.objects.filter(series=series).values_list("pk", flat=True))
        ArchivedMeetingAccess.objects.bulk_create(
            [
                ArchivedMeetingAccess(meeting_id=meeting_id, user_id=access["user_id"], role=access["role"])
                for meeting_id in remaining_meeting_ids
                for access in former_access
            ],
            ignore_conflicts=True,
        )
        Meeting.objects.filter(series=series).update(archived_series_name=name, series=None)
        # The series and its active assignments are removed; archive access
        # remains attached to each retained historical meeting.
        record_event(
            actor=request.user, action="deleted",
            summary=f"Besprechungsreihe „{name}“ gelöscht",
            series=series,
            changes={"Abgeschlossene Termine ebenfalls gelöscht": delete_completed,
                     "Ehemalige Mitglieder mit Lesezugriff": len(former_access) if remaining_meeting_ids else 0},
        )
        series.delete()
    messages.success(
        request,
        f"Die Besprechungsreihe „{name}“ wurde gelöscht. "
        + ("Abgeschlossene Besprechungen wurden ebenfalls entfernt." if delete_completed
           else "Abgeschlossene und sonstige verbleibende Besprechungen samt Protokollen bleiben erhalten.")
    )
    return redirect("series_admin" if is_moderator(request.user) else "dashboard")


@login_required
@moderator_required
@transaction.atomic
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
        messages.error(request, "Dieser Termin gehört zu keiner Besprechungsreihe und kann daher nicht gelöscht werden.")
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
            # Validate every duplicate merge before moving participants or items.
            # A conflict must abort the entire operation without partial changes.
            for source_item in meeting.agenda_items.select_related("topic").order_by("position", "pk"):
                existing_item = target.agenda_items.filter(topic=source_item.topic).first()
                if existing_item is None:
                    continue
                source_child = AgendaItem.objects.filter(followup_of=source_item).first()
                existing_child = AgendaItem.objects.filter(followup_of=existing_item).first()
                if (
                    source_item.followup_of_id and existing_item.followup_of_id
                    and source_item.followup_of_id != existing_item.followup_of_id
                ):
                    messages.error(request, "Der Termin kann nicht gelöscht werden: Zusammengeführte Tagesordnungspunkte haben unterschiedliche Wiedervorlage-Vorgänger.")
                    return redirect("meeting", pk=pk)
                if source_child and existing_child and source_child.pk != existing_child.pk:
                    messages.error(request, "Der Termin kann nicht gelöscht werden: Zusammengeführte Tagesordnungspunkte haben unterschiedliche Wiedervorlage-Nachfolger.")
                    return redirect("meeting", pk=pk)
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
                    status_rank = {"open": 0, "in_progress": 1, "done": 2}
                    if status_rank.get(item.status, 0) > status_rank.get(existing.status, 0):
                        existing.status = item.status
                    previous_followup_id = item.followup_of_id
                    linked_followup = AgendaItem.objects.filter(followup_of=item).first()
                    existing_followup = AgendaItem.objects.filter(followup_of=existing).first()
                    if linked_followup and not existing_followup:
                        linked_followup.followup_of = existing
                        linked_followup.save(update_fields=["followup_of"])
                    if previous_followup_id and not existing.followup_of_id:
                        # Release the predecessor's one-to-one slot before
                        # attaching it to the surviving agenda item.
                        item.followup_of = None
                        item.save(update_fields=["followup_of"])
                        existing.followup_of_id = previous_followup_id
                    existing.save(update_fields=["working_text", "assigned_to", "status", "followup_of"])
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
        record_event(
            actor=request.user, action="deleted",
            summary=f"Besprechungstermin vom {formats.date_format(meeting.date, 'DATE_FORMAT')} aus „{meeting.series.name}“ gelöscht",
            meeting=meeting, series=meeting.series,
            changes={
                "Übertragene Tagesordnungspunkte": moved_count,
                "Zieltermin": target.date.isoformat() if target is not None else None,
                "Teilnehmende übertragen": meeting.participants.count(),
            },
        )
        meeting.delete()

    if moved_count:
        messages.success(request, f"Der Termin wurde gelöscht. {moved_count} Tagesordnungspunkt(e) wurden auf den {formats.date_format(target.date, 'DATE_FORMAT')} übertragen.")
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
    with transaction.atomic():
        meeting = finalize_meeting(meeting)
        record_event(actor=request.user, action="finalized",
                     summary=f"Besprechung „{_meeting_series_name(meeting)}“ vom {formats.date_format(meeting.date, 'DATE_FORMAT')} abgeschlossen",
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
            "topic_title", "text", "status", "topic_id", "responsible_name"
        ))
        # Keep the previous immutable protocol in the append-only audit event.
        # Remove active snapshots so a later completion can create a fresh version.
        meeting.snapshots.all().delete()
        meeting.finalized_at = None
        meeting.save(update_fields=["finalized_at"])
        record_event(
            actor=request.user,
            action="reopened",
            summary=f"Besprechung „{_meeting_series_name(meeting)}“ vom {formats.date_format(meeting.date, 'DATE_FORMAT')} wieder geöffnet",
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
@transaction.atomic
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

@login_required
def user_overview(request):
    """Show and edit the current user's profile, series roles and password."""
    if request.method == "POST" and request.POST.get("form_type") == "access_request":
        series = get_object_or_404(MeetingSeries, pk=request.POST.get("series_id"))
        request_form = SeriesAccessRequestForm(request.POST)
        if request_form.is_valid():
            role_rank = {
                SeriesAccess.ROLE_NONE: -1,
                SeriesAccess.ROLE_READER: 0,
                SeriesAccess.ROLE_PARTICIPANT: 1,
                SeriesAccess.ROLE_MODERATOR: 2,
            }
            current_access = SeriesAccess.objects.filter(user=request.user, series=series).first()
            requested_role = request_form.cleaned_data["role"]
            if current_access and current_access.role == requested_role:
                messages.info(request, "Du hast diese Berechtigung bereits.")
            elif not current_access and requested_role == SeriesAccess.ROLE_NONE:
                messages.info(request, "Du hast für diese Besprechungsreihe bereits keine Berechtigung.")
            elif SeriesAccessRequest.objects.filter(user=request.user, series=series, status=SeriesAccessRequest.STATUS_PENDING).exists():
                messages.error(request, "Für diese Besprechungsreihe liegt bereits ein offener Antrag vor.")
            elif current_access and role_rank[current_access.role] > role_rank[requested_role]:
                # Herabstufungen einschließlich vollständigem Entzug werden automatisch genehmigt.
                with transaction.atomic():
                    if requested_role == SeriesAccess.ROLE_NONE:
                        current_access.delete()
                    else:
                        SeriesAccess.objects.filter(pk=current_access.pk).update(role=requested_role)
                    SeriesAccessRequest.objects.create(
                        user=request.user, series=series,
                        requested_role=requested_role,
                        status=SeriesAccessRequest.STATUS_APPROVED,
                        decision_note="Automatisch genehmigt: Herabstufung der bestehenden Berechtigung.",
                        decided_at=timezone.now(),
                    )
                messages.success(
                    request,
                    "Deine Berechtigung wurde automatisch herabgestuft und ist jetzt wirksam."
                    if requested_role != SeriesAccess.ROLE_NONE
                    else "Deine Berechtigung für diese Besprechungsreihe wurde entfernt.",
                )
            else:
                SeriesAccessRequest.objects.create(
                    user=request.user, series=series,
                    requested_role=requested_role,
                )
                messages.success(request, "Dein Berechtigungsantrag wurde übermittelt.")
            return redirect("user_overview")
        messages.error(request, "Bitte wähle eine gültige Berechtigung.")
    if request.method == "POST" and request.POST.get("form_type") == "password":
        profile_form = PersonalProfileForm(user=request.user)
        password_form = PasswordChangeForm(request.user, request.POST)
    elif request.method == "POST" and request.POST.get("form_type") == "profile":
        profile_form = PersonalProfileForm(request.POST, user=request.user)
        password_form = PasswordChangeForm(request.user)
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, "Deine persönlichen Daten wurden gespeichert.")
            return redirect("user_overview")
        messages.error(request, "Bitte prüfe deine persönlichen Angaben.")
    else:
        profile_form = PersonalProfileForm(user=request.user)
        password_form = PasswordChangeForm(request.user)

    if request.method == "POST" and request.POST.get("form_type") == "password":
        if password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Dein Passwort wurde erfolgreich geändert.")
            return redirect("user_overview")
        messages.error(request, "Bitte prüfe die Angaben zum Passwort.")

    # Prevent autofocus from scrolling the account page to the password section.
    password_form.fields["old_password"].widget.attrs.pop("autofocus", None)

    admin_access = is_admin(request.user)
    assignments = {
        assignment.series_id: assignment
        for assignment in SeriesAccess.objects.filter(user=request.user).select_related("series")
    }
    latest_requests = {}
    for item in SeriesAccessRequest.objects.filter(user=request.user).select_related("series").order_by("-created_at"):
        latest_requests.setdefault(item.series_id, item)
    role_labels = dict(SeriesAccess.ROLE_CHOICES)
    series_rows = []
    for series in MeetingSeries.objects.order_by("name"):
        assignment = assignments.get(series.pk)
        pending = latest_requests.get(series.pk)
        series_rows.append({
            "series": series,
            "role_label": "Admin – globaler Zugriff" if admin_access else (
                role_labels.get(assignment.role, assignment.role) if assignment else "Keine Berechtigung"
            ),
            "role_value": assignment.role if assignment else "",
            "pending_request": pending if pending and pending.status == SeriesAccessRequest.STATUS_PENDING else None,
            "latest_request": pending,
            "can_request": not admin_access and not (pending and pending.status == SeriesAccessRequest.STATUS_PENDING),
        })

    return render(request, "meetings/user_overview.html", {
        "profile_form": profile_form,
        "password_form": password_form,
        "series_rows": series_rows,
        "is_admin_user": admin_access,
        "request_role_choices": SeriesAccess.REQUEST_ROLE_CHOICES,
    })



# ---------------------------------------------------------------------------
# Server-local deployment updates (global administrators only)
# ---------------------------------------------------------------------------
import http.client
import json
import os
import shutil
import socket
import subprocess
from pathlib import Path

from django.views.decorators.http import require_http_methods


UPDATE_SOCKET = os.getenv(
    "MEETING_UPDATER_SOCKET", "/run/meeting-manager-updater/control.sock"
)
UPDATE_STATUS_FILE = Path(
    os.getenv("MEETING_UPDATER_STATUS_FILE", "/var/lib/meeting-manager-updater/status.json")
)
DEBIAN_UPDATE_COMMAND = "/usr/local/sbin/meeting-manager-update"
UPDATE_BRANCHES = {"beta", "main"}


class _UnixSocketHTTPConnection(http.client.HTTPConnection):
    def __init__(self, socket_path, timeout=3):
        super().__init__("localhost", timeout=timeout)
        self.socket_path = socket_path

    def connect(self):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.settimeout(self.timeout)
        self.sock.connect(self.socket_path)


def _updater_request(path, method="GET", payload=None):
    connection = _UnixSocketHTTPConnection(UPDATE_SOCKET)
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {"Content-Type": "application/json"} if body is not None else {}
    try:
        connection.request(method, path, body=body, headers=headers)
        response = connection.getresponse()
        data = json.loads(response.read().decode("utf-8"))
        return response.status, data
    finally:
        connection.close()


def _read_update_status():
    if os.path.exists(UPDATE_SOCKET):
        try:
            code, data = _updater_request("/status")
            if code == 200 and isinstance(data, dict):
                return data
        except (OSError, ValueError, http.client.HTTPException):
            pass
    try:
        data = json.loads(UPDATE_STATUS_FILE.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            if data.get("status") == "running" and not os.path.exists(UPDATE_SOCKET):
                active = subprocess.run(
                    ["/usr/bin/systemctl", "is-active", "--quiet", "meeting-manager-update.service"],
                    capture_output=True, timeout=3, check=False,
                )
                if active.returncode != 0:
                    data = {
                        **data,
                        "status": "error",
                        "message": "Der Update-Dienst ist nicht mehr aktiv. Bitte das Protokoll auf einen Abbruch prüfen.",
                    }
            return data
    except (OSError, ValueError, subprocess.SubprocessError):
        pass
    return {
        "status": "idle",
        "branch": None,
        "started_at": None,
        "finished_at": None,
        "message": "Noch kein Update ausgeführt.",
        "log": "",
    }

def _format_commit_timestamp(value):
    try:
        committed_at = datetime.fromisoformat(value)
        configured_timezone = (
            OrganizationSettings.objects.filter(pk=1)
            .values_list("timezone", flat=True)
            .first()
            or "Europe/Berlin"
        )
        try:
            display_timezone = ZoneInfo(configured_timezone)
        except (ZoneInfoNotFoundError, TypeError, ValueError):
            display_timezone = ZoneInfo("Europe/Berlin")
        return formats.date_format(timezone.localtime(committed_at, display_timezone), 'DATETIME_FORMAT')
    except (TypeError, ValueError):
        return value


def _deployment_info():
    if os.path.exists(UPDATE_SOCKET):
        try:
            code, _status = _updater_request("/status")
            if code != 200:
                raise RuntimeError("Der Docker-Updater antwortet nicht mit einem gültigen Status.")
        except (OSError, ValueError, http.client.HTTPException, RuntimeError) as exc:
            return {
                "deployment_type": "Docker Compose",
                "current_branch": os.getenv("MEETING_BUILD_BRANCH", "unbekannt"),
                "current_commit_date": _format_commit_timestamp(os.getenv("MEETING_BUILD_COMMIT_DATE", "nicht verfügbar")),
                "current_image": "",
                "build_created": "",
                "update_available": False,
                "availability_message": f"Der Docker-Updater ist nicht erreichbar: {exc}",
            }
        return {
            "deployment_type": "Docker Compose",
            "current_branch": os.getenv("MEETING_BUILD_BRANCH", "Im Image nicht hinterlegt"),
            "current_commit_date": _format_commit_timestamp(os.getenv("MEETING_BUILD_COMMIT_DATE", "Im Image nicht hinterlegt")),
            "current_image": "",
            "build_created": "",
            "update_available": True,
            "availability_message": "",
        }

    if os.path.isfile(DEBIAN_UPDATE_COMMAND) and shutil.which("sudo"):
        def git_value(*args):
            try:
                result = subprocess.run(
                    ["/usr/bin/git", "-c", "safe.directory=/opt/meeting-manager", "-C", "/opt/meeting-manager", *args],
                    text=True, capture_output=True, timeout=3, check=True,
                )
                return result.stdout.strip()
            except (OSError, subprocess.SubprocessError):
                return "nicht verfügbar"

        return {
            "deployment_type": "Debian / systemd",
            "current_branch": git_value("branch", "--show-current"),
            "current_commit_date": _format_commit_timestamp(git_value("show", "-s", "--format=%cI", "HEAD")),
            "current_commit_message": git_value("show", "-s", "--format=%s", "HEAD"),
            "current_image": "",
            "build_created": "",
            "update_available": True,
            "availability_message": "",
        }

    return {
        "deployment_type": "Nicht eingerichtet",
        "current_branch": "unbekannt",
        "current_commit_date": "nicht verfügbar",
        "current_image": "",
        "build_created": "",
        "update_available": False,
        "availability_message": (
            "Es wurde kein lokaler Updater gefunden. Auf Debian muss die aktualisierte "
            "Systemkonfiguration installiert sein; bei Docker muss der Host-Updater "
            "eingerichtet und sein Socket in den App-Container eingebunden sein."
        ),
    }

@login_required
@require_http_methods(["GET", "POST"])
def deployment_updates(request):
    if not is_admin(request.user):
        return HttpResponseForbidden("Nur globale Administratoren dürfen Updates verwalten.")

    info = _deployment_info()
    if request.method == "POST":
        branch = request.POST.get("branch", "")
        if branch not in UPDATE_BRANCHES:
            messages.error(request, "Bitte ausschließlich beta oder main auswählen.")
            return redirect("deployment_updates")
        if not info["update_available"]:
            messages.error(request, info["availability_message"])
            return redirect("deployment_updates")

        status = _read_update_status()
        if status.get("status") == "running":
            messages.warning(request, "Es läuft bereits ein Update.")
            return redirect("deployment_updates")

        try:
            if os.path.exists(UPDATE_SOCKET):
                code, result = _updater_request("/update", method="POST", payload={"branch": branch})
                if code != 202:
                    raise RuntimeError(result.get("error", "Der Docker-Updater hat das Update abgelehnt."))
            else:
                started = subprocess.run(
                    ["sudo", "-n", DEBIAN_UPDATE_COMMAND, branch],
                    stdin=subprocess.DEVNULL,
                    capture_output=True,
                    text=True,
                    timeout=10,
                    check=False,
                )
                if started.returncode != 0:
                    raise RuntimeError(started.stderr.strip() or "Der Debian-Updater konnte nicht gestartet werden.")
            messages.success(
                request,
                f"Das Update auf {branch} wurde gestartet. Die Ausführung erfolgt unabhängig von dieser Webseite.",
            )
        except (OSError, RuntimeError, subprocess.SubprocessError, http.client.HTTPException, ValueError) as exc:
            messages.error(request, f"Das Update konnte nicht gestartet werden: {exc}")
        return redirect("deployment_updates")

    update_status = _read_update_status()
    for timestamp_field in ("started_at", "finished_at"):
        if update_status.get(timestamp_field):
            update_status[timestamp_field] = _format_commit_timestamp(update_status[timestamp_field])

    return render(request, "meetings/deployment_updates.html", {
        **info,
        "update_status": update_status,
    })
