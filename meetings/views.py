from datetime import date, datetime, timedelta
from functools import wraps
from io import BytesIO
import logging
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from urllib.parse import quote, urlencode
from xml.sax.saxutils import escape

from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth import login, logout, get_user_model, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.forms import SetPasswordForm, PasswordChangeForm
from django.db import transaction, models
from django.db.models import F, Q, Window, Prefetch, Min, OuterRef, Subquery, Count
from django.db.models.functions import RowNumber, Coalesce
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import formats, timezone
from django.utils.text import slugify
from django.utils.http import url_has_allowed_host_and_scheme
from .forms import PersonalProfileForm, SeriesAccessRequestForm, UsernameLoginForm, TopicCommentForm, AgendaTextForm, AttachmentForm, SeriesForm, MeetingParticipantsForm, MeetingDateForm, AgendaItemCreateForm, AgendaScheduleForm, UserDisplayModelChoiceField
from .models import Meeting, MeetingSeries, Topic, TopicAttachment, TopicTransferHistory, AuditEvent, AgendaItem, OrganizationSettings, TopicComment, ArchivedMeetingAccess, RetainedAgendaEntry
from .audit import record_event, record_transfer_events
from .services import ensure_agenda, generate_meetings, finalize_meeting
from .access import accessible_meetings, accessible_series, accessible_topics, auditor_readonly, has_writable_series, is_admin, is_auditor, is_moderator, is_reader
from .models import SeriesAccess, SeriesAccessRequest
from .user_display import user_display_name

logger = logging.getLogger(__name__)

def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    if not UserModel.objects.exists():
        return redirect("setup_wizard")
    form = UsernameLoginForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        # Persistent sessions are deliberately capped at the configured eight-hour
        # lifetime. "Angemeldet bleiben" only keeps the session after browser close;
        # it must not silently extend the authentication lifetime to 30 days.
        request.session.set_expiry(8 * 60 * 60 if request.POST.get("remember_me") else 0)
        next_url = request.POST.get("next") or request.GET.get("next", "")
        if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
            return redirect(next_url)
        return redirect("dashboard")
    return render(request, "meetings/login.html", {"form": form, "next": request.GET.get("next", ""), "show_password": bool(request.POST.get("username"))})

@login_required
def forced_password_change(request):
    from .models import UserProfile
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.user.has_usable_password() and not profile.must_change_password:
        return redirect("dashboard")
    if not profile.must_change_password:
        profile.must_change_password = True
        profile.save(update_fields=["must_change_password"])
    form = SetPasswordForm(user=request.user, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        profile.must_change_password = False
        profile.password_setup_expires_at = None
        profile.save(update_fields=["must_change_password", "password_setup_expires_at"])
        update_session_auth_hash(request, user)
        AuditEvent.objects.create(
            actor=user,
            scope=AuditEvent.SCOPE_SYSTEM,
            action="updated",
            summary=f"Passwort für Benutzerkonto „{user.username}“ neu festgelegt",
            changes={"Passwortstatus": {"nachher": "Passwort durch Nutzer neu festgelegt"}},
        )
        messages.success(request, "Ihr neues Passwort wurde gespeichert.")
        return redirect("dashboard")
    return render(request, "meetings/forced_password_change.html", {"form": form})


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
    if view.__name__ in {"series_edit", "series_delete", "series_delete_future", "series_extend", "series_reset_meetings"}:
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
        allowed = (
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
            if series is None:
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
        if series is None or is_reader(request.user, series):
            return HttpResponseForbidden("Für diese Besprechungsreihe bestehen ausschließlich Leserechte.")
        return view(request, *args, **kwargs)
    return wrapped


def admin_only(user):
    return is_admin(user)

@login_required
def dashboard(request):
    if is_auditor(request.user):
        return redirect("auditor_overview")
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
    search_query = query.casefold()
    selected_status = request.GET.get("status", "all" if is_reader(request.user) and not has_writable_series(request.user) else "active")
    selected_series = request.GET.get("series", "")
    selected_assignee = request.GET.get("assigned_to", "" if is_reader(request.user) else str(request.user.pk))
    selected_due = request.GET.get("due", "next_week")

    # A search is independent of all dashboard filters.
    # Apply the filters only when no search term was submitted.
    if query:
        topics = topics.filter(
            Q(title__icontains=search_query)
            | Q(agenda_items__working_text__icontains=search_query)
            | Q(comments__body__icontains=search_query)
            | Q(series__name__icontains=search_query)
            | Q(agenda_items__assigned_to__username__icontains=search_query)
            | Q(agenda_items__assigned_to__first_name__icontains=search_query)
            | Q(agenda_items__assigned_to__last_name__icontains=search_query)
        )
        selected_status = "all"
        selected_series = ""
        selected_assignee = ""
        selected_due = ""
    else:
        if selected_status == "active":
            topics = topics.filter(agenda_items__status__in=["open", "in_progress"])
        elif selected_status in {"open", "in_progress", "done"}:
            topics = topics.filter(agenda_items__status=selected_status)
        elif selected_status != "all":
            selected_status = "active"
            topics = topics.filter(agenda_items__status__in=["open", "in_progress"])

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
        "new_topic_series": accessible_series(request.user).exclude(
            user_access__role=SeriesAccess.ROLE_READER
        ).filter(active=True).distinct().order_by("name"),
        "new_topic_meetings": accessible_meetings(request.user).filter(
            series__in=accessible_series(request.user).filter(active=True),
            date__gte=today, finalized_at__isnull=True,
        ).select_related("series").order_by("series__name", "date"),
        "result_count": topics.count(),
        "is_admin_user": is_admin(request.user),
    })


@login_required
def meetings_overview(request):
    """Show only meetings belonging to series the current user may access."""
    if is_auditor(request.user):
        return redirect("auditor_overview")
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
    role_by_series = {
        access.series_id: role_labels.get(access.role, access.role)
        for access in SeriesAccess.objects.filter(user=request.user, series__in=series)
    }

    events = []
    for meeting in meetings:
        role = role_by_series.get(meeting.series_id, "")
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
            "role": role_by_series.get(item.pk, ""),
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
    ).filter(
        Q(meeting__date__lt=today)
        | Q(meeting__date=today, meeting__finalized_at__isnull=False)
    ).filter(pk__in=Subquery(latest_item_ids)).select_related(
        "topic", "topic__series", "meeting", "assigned_to"
    ).order_by("topic__series__name", "topic__title")
    topics_without_items = Topic.objects.filter(
        series__in=allowed_series,
        status__in=["open", "in_progress"],
        agenda_items__isnull=True,
    ).select_related("series", "assigned_to").order_by("series__name", "title")

    if request.method == "POST":
        target_meeting_id = request.POST.get("target_meeting")
        if request.POST.get("schedule_topic"):
            topic = get_object_or_404(topics_without_items, pk=request.POST.get("schedule_topic"))
            target_meeting = get_object_or_404(
                Meeting.objects.filter(series=topic.series, date__gt=today, finalized_at__isnull=True),
                pk=target_meeting_id,
            )
            with transaction.atomic():
                next_position = (
                    target_meeting.agenda_items.order_by("-position").values_list("position", flat=True).first()
                )
                AgendaItem.objects.create(
                    meeting=target_meeting,
                    topic=topic,
                    status=topic.status if topic.status in {"open", "in_progress"} else "open",
                    position=(next_position if next_position is not None else -1) + 1,
                )
                record_event(
                    actor=request.user, action="updated",
                    summary=f"„{topic.title}“ erstmals auf die Tagesordnung am {formats.date_format(target_meeting.date, 'DATE_FORMAT')} gesetzt",
                    topic=topic, meeting=target_meeting,
                    changes={"Tagesordnung": {"nachher": target_meeting.date.isoformat()}},
                )
            messages.success(request, f"„{topic.title}“ wurde auf die Tagesordnung am {formats.date_format(target_meeting.date, 'DATE_FORMAT')} gesetzt.")
            return redirect("open_topics")

        item = get_object_or_404(items, pk=request.POST.get("schedule_item"))
        target_meeting = get_object_or_404(
            Meeting.objects.filter(series=item.topic.series, date__gt=today, finalized_at__isnull=True),
            pk=target_meeting_id,
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
        rows.append({
            "item": item, "topic": item.topic, "status_display": item.get_status_display(),
            "future_meetings": future_meetings,
        })
    for topic in topics_without_items:
        future_meetings = Meeting.objects.filter(
            series=topic.series, date__gt=today, finalized_at__isnull=True
        ).order_by("date")
        rows.append({
            "item": None, "topic": topic, "status_display": topic.get_status_display(),
            "future_meetings": future_meetings,
        })
    rows.sort(key=lambda row: (row["topic"].series.name.casefold(), row["topic"].title.casefold()))
    return render(request, "meetings/open_topics.html", {"rows": rows, "today": today})

@login_required
def my_tasks(request):
    """Separate topic-level ownership from explicit agenda-item assignments."""
    if is_auditor(request.user):
        return redirect("auditor_overview")
    today = timezone.localdate()
    visible_meetings = accessible_meetings(request.user)
    series_options = accessible_series(request.user).order_by("name")
    selected_series = request.GET.get("series", "")
    selected_series_id = None
    if selected_series.isdigit() and series_options.filter(pk=int(selected_series)).exists():
        selected_series_id = int(selected_series)
    else:
        selected_series = ""

    agenda_dates = AgendaItem.objects.filter(
        topic=OuterRef("pk"),
        meeting__in=visible_meetings,
        meeting__finalized_at__isnull=True,
    )
    if selected_series_id:
        agenda_dates = agenda_dates.filter(meeting__series_id=selected_series_id)
    upcoming_agenda_date = agenda_dates.filter(
        meeting__date__gte=today
    ).order_by("meeting__date", "pk").values("meeting__date")[:1]
    latest_past_agenda_date = agenda_dates.filter(
        meeting__date__lt=today
    ).order_by("-meeting__date", "-pk").values("meeting__date")[:1]

    latest_agenda_query = AgendaItem.objects.filter(
        topic=OuterRef("pk"), meeting__in=visible_meetings
    )
    if selected_series_id:
        latest_agenda_query = latest_agenda_query.filter(
            meeting__series_id=selected_series_id
        )

    main_topics_query = accessible_topics(request.user).filter(
        assigned_to=request.user, status__in=["open", "in_progress"]
    ).select_related("series").annotate(
        # A scheduled upcoming meeting takes precedence over old unfinished agenda entries.
        # Only fall back to the latest past meeting when no future appointment exists.
        next_meeting_date=Coalesce(
            Subquery(upcoming_agenda_date),
            Subquery(latest_past_agenda_date),
        ),
        latest_agenda_text=Subquery(
            latest_agenda_query.order_by("-meeting__date", "-pk")
            .values("working_text")[:1]
        ),
    )
    if selected_series_id:
        main_topics_query = main_topics_query.filter(series_id=selected_series_id)
    main_topics = list(main_topics_query.distinct().order_by(
        F("next_meeting_date").asc(nulls_last=True), "title"
    ))

    agenda_tasks_query = AgendaItem.objects.filter(
        meeting__in=visible_meetings,
        meeting__date__gte=today,
        meeting__finalized_at__isnull=True,
        assigned_to=request.user,
        status__in=["open", "in_progress"],
    ).select_related("topic", "topic__series", "meeting")
    if selected_series_id:
        agenda_tasks_query = agenda_tasks_query.filter(meeting__series_id=selected_series_id)
    agenda_tasks = list(agenda_tasks_query.order_by(
        "meeting__date", "meeting__series__name", "position", "pk"
    ))

    return render(request, "meetings/my_tasks.html", {
        "topics": main_topics,
        "main_topics": main_topics,
        "agenda_tasks": agenda_tasks,
        "today": today,
        "selected_series": selected_series,
        "series_options": series_options,
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
            followup.working_text = ""
            followup.status = item.status
            followup.assigned_to_id = item.assigned_to_id
            followup.position = next_position
            followup.carried_forward = True
            followup.save(update_fields=["meeting", "working_text", "status", "assigned_to", "position", "carried_forward"])
        else:
            AgendaItem.objects.create(meeting=target_meeting, topic=topic, working_text="", assigned_to_id=item.assigned_to_id, status=item.status, position=next_position, carried_forward=True, followup_of=item)
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
        is_auditor(request.user) or (meeting.series_id is None
        and ArchivedMeetingAccess.objects.filter(meeting=meeting, user=request.user).exists())
    )
    if not meeting.participants_initialized and not meeting.finalized_at and not archived_readonly:
        if not meeting.participants.exists() and meeting.series_id:
            default_participants = SeriesAccess.objects.filter(
                series=meeting.series, user__is_active=True
            ).exclude(role=SeriesAccess.ROLE_READER).values_list("user_id", flat=True)
            meeting.participants.set(default_participants)
        meeting.participants_initialized = True
        meeting.save(update_fields=["participants_initialized"])
    items = (
        meeting.agenda_items.select_related("topic", "assigned_to").all()
        if is_auditor(request.user) else ensure_agenda(meeting)
    )
    participants = meeting.participants.filter(is_active=True).order_by("last_name", "first_name", "username")
    assignees = UserModel.objects.filter(is_active=True).order_by("last_name", "first_name", "username")
    writable_series = accessible_series(request.user)
    if is_auditor(request.user):
        writable_series = MeetingSeries.objects.none()
    else:
        writable_series = writable_series.exclude(user_access__role=SeriesAccess.ROLE_READER)
    writable_series = writable_series.filter(active=True).order_by("name")
    target_meetings = accessible_meetings(request.user).filter(
        series__in=writable_series, date__gt=meeting.date, finalized_at__isnull=True
    ).select_related("series").order_by("series__name", "date")

    if request.method == "POST":
        if is_auditor(request.user):
            return HttpResponseForbidden("Auditor*innen haben ausschließlich Lesezugriff.")
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
                    "is_moderator": meeting.series_id is not None and is_moderator(request.user, meeting.series),
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
        elif request.POST.get("schedule_item") and not request.POST.get("save_all_working_texts") and not request.POST.get("target_meeting"):
            item = get_object_or_404(
                AgendaItem.objects.select_related("topic"),
                pk=request.POST.get("schedule_item"), meeting=meeting,
            )
            item.working_text = request.POST.get("working_text", item.working_text)
            followup = AgendaItem.objects.filter(followup_of=item).first()
            if followup and request.POST.get("confirm_clear_followup") != "1":
                messages.error(request, "Bitte bestätige das Entfernen der bestehenden Wiedervorlage.")
            else:
                with transaction.atomic():
                    item.save(update_fields=["working_text"])
                    if followup:
                        followup_meeting = followup.meeting
                        followup.delete()
                        record_event(
                            actor=request.user, action="updated",
                            summary=f"Wiedervorlage für „{item.topic.title}“ entfernt",
                            topic=item.topic, meeting=meeting,
                            changes={"Wiedervorlage": {
                                "vorher": followup_meeting.date.isoformat(),
                                "nachher": None,
                            }},
                        )
                        messages.success(request, f"Die Wiedervorlage für „{item.topic.title}“ wurde entfernt.")
                    else:
                        messages.success(request, "Text gespeichert.")
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
                if not title:
                    messages.error(request, "Bitte gib einen Thementitel ein.")
                else:
                    topic = Topic.objects.create(
                        title=title, series=meeting.series,
                        assigned_to=create_form.cleaned_data["primary_assigned_to"],
                    )
                    AgendaItem.objects.create(
                        meeting=meeting, topic=topic, working_text="",
                        assigned_to=create_form.cleaned_data["assigned_to"],
                        position=(meeting.agenda_items.order_by("-position").values_list("position", flat=True).first() if meeting.agenda_items.exists() else -1) + 1,
                    )
                    record_event(
                        actor=request.user, action="created",
                        summary=f"Thema „{topic.title}“ zur Tagesordnung am {formats.date_format(meeting.date, 'DATE_FORMAT')} hinzugefügt",
                        topic=topic, meeting=meeting,
                        changes={
                            "Titel": {"vorher": None, "nachher": topic.title},
                            "Hauptzuständigkeit": {
                                "vorher": None,
                                "nachher": user_display_name(topic.assigned_to) if topic.assigned_to else None,
                            },
                        },
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
        "is_moderator": meeting.series_id is not None and is_moderator(request.user, meeting.series),
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
        }
    # Topic-owned agenda text survives deletion of its original meeting.
    for entry in RetainedAgendaEntry.objects.filter(topic=item.topic).order_by("-meeting_date", "position", "pk"):
        history[f"deleted-{entry.pk}"] = {
            "series": entry.series_name or "Besprechung",
            "date": entry.meeting_date,
            "text": entry.working_text,
            "responsible": entry.responsible_name,
            "meeting_deleted": True,
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
    if is_auditor(request.user):
        return redirect("auditor_overview")
    from .agenda_topic_views import _topic_archive_state

    archivable_topics = []
    topics = accessible_topics(request.user).filter(status="done").select_related("series", "assigned_to").prefetch_related("agenda_items__meeting").order_by("title")
    for topic in topics:
        if topic.series_id is None or not is_moderator(request.user, topic.series):
            continue
        if topic.status == "done":
            can_archive, _reason = _topic_archive_state(topic)
            if not can_archive:
                continue
            if topic.agenda_items.filter(meeting__finalized_at__isnull=True).exists():
                continue
        archivable_topics.append(topic)

    from .retention import effective_retention_years, topic_deletion_date
    archived_topics = accessible_topics(request.user).filter(status="archived").select_related("series").order_by("title")
    for archived_topic in archived_topics:
        archived_topic.retention_effective_years = effective_retention_years(archived_topic)
        archived_topic.deletion_date = topic_deletion_date(archived_topic)
    return render(request, "meetings/archive.html", {
        "archivable_topics": archivable_topics,
        "archived_topics": archived_topics,
    })

@login_required
@reader_no_access
@transaction.atomic
def attachment_add(request, pk):
    topic = get_object_or_404(accessible_topics(request.user), pk=pk)
    if topic.series_id is None:
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
        next_url = request.POST.get("next", "")
        if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
            return redirect(next_url)
        return redirect("topic_edit", pk=pk)
    return render(request, "meetings/attachment_form.html", {"form": form, "topic": topic})


@login_required
@login_required
def organization_logo(request):
    """Serve the configured organization logo to signed-in application users."""
    organization = OrganizationSettings.objects.filter(pk=1).first()
    if not organization or not organization.logo:
        from django.http import Http404
        raise Http404("Es ist kein Organisationslogo hinterlegt.")
    from .secure_files import serve_organization_logo
    return serve_organization_logo(organization.logo)


@login_required
@auditor_readonly
def agenda_attachment_add(request, meeting_pk, item_pk):
    """Add an attachment from the agenda item's attachment dialog."""
    if request.method != "POST":
        return HttpResponseForbidden("Diese Aktion ist nur per POST möglich.")

    meeting = get_object_or_404(accessible_meetings(request.user), pk=meeting_pk)
    item = get_object_or_404(
        AgendaItem.objects.select_related("topic", "topic__series"),
        pk=item_pk, meeting=meeting,
        topic__in=accessible_topics(request.user),
    )
    topic = item.topic
    if (
        is_reader(request.user, topic.series)
        or topic.series_id is None
    ):
        return HttpResponseForbidden("Für diese Anlage fehlen Schreibrechte.")

    form = AttachmentForm(request.POST, request.FILES)
    if form.is_valid():
        attachment = form.save(commit=False)
        attachment.topic = topic
        attachment.save()
        record_event(
            actor=request.user,
            action="attachment_added",
            summary=f"Anlage „{attachment.label}“ zu „{topic.title}“ hinzugefügt",
            topic=topic,
            meeting=meeting,
            changes={
                "Bezeichnung": attachment.label,
                "Datei": attachment.uploaded_file.name if attachment.uploaded_file else None,
                "Netzwerkpfad": attachment.network_path or None,
            },
        )
        messages.success(request, "Anlage hinzugefügt.")
    else:
        messages.error(request, "Die Anlage konnte nicht hinzugefügt werden. Bitte prüfe Bezeichnung, Datei und Netzwerkpfad.")
    return redirect(reverse("meeting", args=[meeting.pk]) + f"?attachments={item.pk}#agenda-item-{item.pk}")


@login_required
@auditor_readonly
def attachment_delete(request, pk):
    """Delete one topic attachment, including its uploaded file when present."""
    if request.method != "POST":
        return HttpResponseForbidden("Diese Aktion ist nur per POST möglich.")

    attachment = get_object_or_404(
        TopicAttachment.objects.select_related("topic__series"),
        pk=pk,
        topic__in=accessible_topics(request.user),
    )
    topic = attachment.topic
    if (
        topic.series_id is None
        or (topic.series_id is not None and is_reader(request.user, topic.series))
    ):
        return HttpResponseForbidden("Für diese Anlage fehlen Schreibrechte.")

    file_name = attachment.uploaded_file.name if attachment.uploaded_file else ""
    storage = attachment.uploaded_file.storage if file_name else None
    label = attachment.label
    with transaction.atomic():
        record_event(
            actor=request.user,
            action="deleted",
            summary=f"Anlage „{label}“ von „{topic.title}“ gelöscht",
            topic=topic,
            changes={"Anlage": label, "Datei": file_name or None, "Netzwerkpfad": attachment.network_path or None},
        )
        attachment.delete()
        if file_name:
            storage.delete(file_name)

    messages.success(request, f"Anlage „{label}“ wurde gelöscht.")
    next_url = request.POST.get("next") or request.GET.get("next", "")
    if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
        return redirect(next_url)
    return redirect("topic_edit", pk=topic.pk)


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
                "followup_date": snapshot.followup_date,
                "followup_series_name": snapshot.followup_series_name,
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
            "followup_series_name": (
                _meeting_series_name(item.followup_item.meeting)
                if hasattr(item, "followup_item") else ""
            ),
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
    # Keep the series name recognizable while removing characters that are
    # invalid in Windows filenames. The meeting date is the agenda date,
    # not the date on which the PDF is generated or downloaded.
    series = "".join(
        char if char.isalnum() or char in " _-" else "_"
        for char in _meeting_series_name(meeting)
    ).strip(" ._") or "Besprechung"
    return f"Protokoll_{series}_{meeting.date:%Y-%m-%d}.{extension}"


@login_required
def protocol_pdf(request, pk):
    meeting = get_object_or_404(accessible_meetings(request.user).select_related("series"), pk=pk)
    entries = _protocol_entries(meeting)

    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.lib.utils import ImageReader
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.pdfgen import canvas as pdf_canvas
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, KeepTogether, HRFlowable

    organization = OrganizationSettings.objects.filter(pk=1).first()
    organization_name = organization.name.strip() if organization and organization.name else ""
    brand = OrganizationSettings.current_brand_colors()

    # Resolve the logo from the configured Django storage and fail visibly if
    # a configured logo cannot be embedded. A silent fallback produced PDFs
    # that looked valid but unexpectedly omitted the organization's branding.
    organization_logo_image = None
    logo_is_configured = bool(organization and organization.logo and organization.logo.name)
    if logo_is_configured:
        logo_field = organization.logo
        is_svg = logo_field.name.lower().endswith(".svg")
        prepared_logo = organization.logo_png if is_svg else logo_field
        if is_svg and not prepared_logo:
            logger.error(
                "Protokoll-PDF: Für das konfigurierte SVG-Logo (organization_id=%s, name=%s) "
                "liegt keine vorbereitete PNG-Version vor.",
                organization.pk, logo_field.name,
            )
            return HttpResponse(
                "Das konfigurierte Organisationslogo konnte nicht geladen und in das "
                "Protokoll-PDF eingebettet werden. Bitte laden Sie das Logo unter "
                "Verwaltung erneut hoch oder entfernen Sie es vorübergehend.",
                status=503,
                content_type="text/plain; charset=utf-8",
            )
        logger.info(
            "Protokoll-PDF: Organisationslogo konfiguriert (organization_id=%s, "
            "name=%s, storage=%s).",
            organization.pk, prepared_logo.name, prepared_logo.storage.__class__.__name__,
        )
        try:
            prepared_logo.open("rb")
            try:
                logo_data = prepared_logo.read()
            finally:
                prepared_logo.close()

            if not logo_data:
                raise ValueError("Die gespeicherte Logodatei ist leer.")

            logo_reader = ImageReader(BytesIO(logo_data))
            logo_width_px, logo_height_px = logo_reader.getSize()
            if not logo_width_px or not logo_height_px:
                raise ValueError("Das Organisationslogo hat ungültige Abmessungen.")
            organization_logo_image = logo_reader
            logger.info(
                "Protokoll-PDF: Organisationslogo erfolgreich dekodiert (%sx%s px).",
                logo_width_px, logo_height_px,
            )
        except Exception as exc:
            logger.exception(
                "Protokoll-PDF: Organisationslogo %r (organization_id=%s) "
                "konnte aus Storage %s nicht geladen/eingebettet werden.",
                logo_field.name, organization.pk, logo_field.storage.__class__.__name__,
            )
            return HttpResponse(
                "Das konfigurierte Organisationslogo konnte nicht geladen und in das "
                "Protokoll-PDF eingebettet werden. Bitte laden Sie das Logo unter "
                "Verwaltung erneut hoch oder entfernen Sie es vorübergehend.",
                status=503,
                content_type="text/plain; charset=utf-8",
            )
    else:
        logger.warning(
            "Protokoll-PDF: Kein Organisationslogo konfiguriert (organization_id=%s).",
            organization.pk if organization else None,
        )

    def brand_color(value, fallback):
        try:
            return colors.HexColor(value)
        except (TypeError, ValueError):
            return colors.HexColor(fallback)

    primary = brand_color(brand.get("primary_color"), "#00549F")
    secondary = brand_color(brand.get("secondary_color"), "#8FC5FF")
    buffer = BytesIO()
    left_margin = right_margin = 20 * mm
    top_margin, bottom_margin = 36 * mm, 25 * mm
    document = SimpleDocTemplate(
        buffer, pagesize=A4, rightMargin=right_margin, leftMargin=left_margin,
        topMargin=top_margin, bottomMargin=bottom_margin,
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

    created_at = timezone.localtime(timezone.now())
    finalized_label = (
        "Gesicherter Protokollstand · " + formats.date_format(timezone.localtime(meeting.finalized_at), "DATETIME_FORMAT")
        if meeting.finalized_at else "Entwurf – nicht abgeschlossen"
    )
    created_label = formats.date_format(created_at, "DATETIME_FORMAT")
    series_name = _meeting_series_name(meeting)
    meeting_date = formats.date_format(meeting.date, "DATE_FORMAT")

    story = [
        Paragraph("Teilnehmer*innen", styles["ProtocolSection"]),
        Paragraph(
            " · ".join(escape(name) for name in _meeting_participant_names(meeting))
            or "Keine Teilnehmer eingetragen.",
            styles["ProtocolBody"],
        ),
        HRFlowable(width="100%", thickness=0.8, color=secondary, spaceBefore=1 * mm, spaceAfter=2 * mm),
        Paragraph("Tagesordnung und Ergebnisse", styles["ProtocolSection"]),
    ]
    for index, entry in enumerate(entries, start=1):
        parts = [Paragraph(f"{index:02d} &nbsp; {escape(entry['title'])}", styles["ProtocolTopic"])]
        status_and_responsible = "<b>Status:</b> " + escape(entry["status"])
        if entry.get("responsible"):
            status_and_responsible += " &nbsp;&nbsp; <b>Verantwortlich:</b> " + escape(entry["responsible"])
        parts.append(Paragraph(status_and_responsible, styles["ProtocolStatus"]))
        parts.append(Paragraph(escape(entry["text"] or "—").replace("\n", "<br/>"), styles["ProtocolBody"]))
        if entry.get("followup_date"):
            followup_label = formats.date_format(entry["followup_date"], "DATE_FORMAT")
            followup_series = escape(entry.get("followup_series_name") or "Gelöschte Besprechungsreihe")
            parts.append(Paragraph(
                "<b>Wiedervorlage:</b> " + followup_series + " " + escape(followup_label),
                styles["ProtocolSmall"],
            ))
        parts.append(Spacer(1, 2 * mm))
        story.append(KeepTogether(parts))
    if not entries:
        story.append(Paragraph("Keine Tagesordnungspunkte vorhanden.", styles["ProtocolSmall"]))

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
                self._draw_running_matter(page_count)
                super().showPage()
            super().save()

        def _draw_running_matter(self, page_count):
            self.saveState()
            page_top = A4[1] - 11 * mm
            right_edge = A4[0] - right_margin
            if organization_logo_image:
                source_width, source_height = organization_logo_image.getSize()
                max_logo_height, max_logo_width = 18 * mm, 42 * mm
                scale = min(max_logo_height / source_height, max_logo_width / source_width)
                logo_width, logo_height = source_width * scale, source_height * scale
                self.drawImage(
                    organization_logo_image, right_edge - logo_width, page_top - logo_height,
                    width=logo_width, height=logo_height, mask="auto",
                )

            self.setFillColor(colors.HexColor("#263445"))
            self.setFont(bold_font, 8.5)
            if organization_name:
                self.drawString(left_margin, page_top - 2 * mm, organization_name[:75])
            self.setFillColor(primary)
            self.setFont(bold_font, 13)
            self.drawCentredString(A4[0] / 2, page_top - 3 * mm, "PROTOKOLL")
            self.setFillColor(colors.HexColor("#526170"))
            self.setFont(regular_font, 9.5)
            self.drawCentredString(
                A4[0] / 2, page_top - 10 * mm,
                f"{series_name} · {meeting_date}",
            )

            self.setStrokeColor(primary)
            self.setLineWidth(1.1)
            self.line(left_margin, A4[1] - 32 * mm, right_edge, A4[1] - 32 * mm)

            footer_y = 15 * mm
            self.setStrokeColor(colors.HexColor("#DCE3EA"))
            self.setLineWidth(0.5)
            self.line(left_margin, footer_y + 4 * mm, right_edge, footer_y + 4 * mm)
            self.setFillColor(colors.HexColor("#687684"))
            self.setFont(regular_font, 7)
            self.drawString(left_margin, footer_y, f"Protokollstand: {finalized_label}"[:105])
            self.drawString(left_margin, footer_y - 4 * mm, f"PDF erstellt: {created_label}"[:105])
            self.setFillColor(colors.HexColor("#263445"))
            self.setFont(bold_font, 7.5)
            self.drawRightString(right_edge, footer_y - 1 * mm, f"Seite {self._pageNumber} von {page_count}")
            self.restoreState()

    document.build(story, canvasmaker=NumberedCanvas)
    pdf_content = buffer.getvalue()
    if logo_is_configured and b"/Subtype /Image" not in pdf_content:
        logger.error(
            "Protokoll-PDF: Logo %r wurde geladen, aber ReportLab hat kein Bildobjekt "
            "in die PDF geschrieben (meeting_id=%s).",
            organization.logo.name, meeting.pk,
        )
        return HttpResponse(
            "Das Organisationslogo wurde geladen, aber nicht in die PDF eingebettet. "
            "Bitte prüfen Sie die Logo-Datei und laden Sie sie erneut hoch.",
            status=503,
            content_type="text/plain; charset=utf-8",
        )
    response = HttpResponse(pdf_content, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{_protocol_filename(meeting, "pdf")}"'
    return response

@login_required
def protocol(request, pk):
    meeting = get_object_or_404(accessible_meetings(request.user), pk=pk)
    if not is_auditor(request.user):
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
        "protocol_filename": _protocol_filename(meeting, "pdf"),
        "can_reopen_meeting": meeting.series_id is not None and is_moderator(request.user, meeting.series),
    })

@login_required
def series_admin(request):
    # Globale Admins dürfen Reihen anlegen und Berechtigungsanträge verwalten,
    # ohne dadurch Zugriff auf bestehende Serieninhalte zu erhalten.
    if not is_admin(request.user) and not is_moderator(request.user):
        return HttpResponseForbidden("Für die Besprechungsserienverwaltung fehlen Moderatorrechte.")
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
    # Die Serienübersicht zeigt ausschließlich Reihen, in denen der angemeldete
    # Benutzer tatsächlich Moderator ist. Admins dürfen Reihen anlegen, erhalten
    # dadurch aber keine pauschalen Serienrechte.
    series_queryset = accessible_series(request.user).filter(
        user_access__user=request.user,
        user_access__role=SeriesAccess.ROLE_MODERATOR,
    )
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
    if is_admin(request.user):
        form.fields["initial_moderator"] = UserDisplayModelChoiceField(
            queryset=UserModel.objects.filter(is_active=True).order_by("last_name", "first_name", "username"),
            label="Moderator der Besprechungsreihe",
            required=True,
            help_text="Diese Person erhält für die neue Reihe automatisch die Moderatorberechtigung.",
        )
    if request.method == "POST" and form.is_valid():
        item = form.save(commit=False)
        selected_moderator = form.cleaned_data.get("initial_moderator") if is_admin(request.user) else request.user
        if not item.end_date:
            item.end_date = date(today.year + 1, 12, 31)
        with transaction.atomic():
            item.save()
            SeriesAccess.objects.update_or_create(
                user=selected_moderator, series=item,
                defaults={"role": SeriesAccess.ROLE_MODERATOR},
            )
            created_meetings = generate_meetings(item)
            AuditEvent.objects.create(
                actor=request.user,
                scope=AuditEvent.SCOPE_SYSTEM,
                action="created",
                summary=f"Besprechungsreihe „{item.name}“ angelegt",
                changes={
                    "Bezeichnung": {"nachher": item.name},
                    "Wiederholung": {"nachher": item.recurrence},
                    "Intervall": {"nachher": item.recurrence_interval},
                    "Wochentag": {"nachher": item.weekday},
                    "Startdatum": {"nachher": item.start_date.isoformat()},
                    "Enddatum": {"nachher": item.end_date.isoformat() if item.end_date else None},
                    "Erster Moderator": {"nachher": selected_moderator.get_full_name() or selected_moderator.username},
                    "Angelegte Termine": {"nachher": len(created_meetings)},
                },
            )
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
                    "Erster Moderator": {"vorher": None, "nachher": selected_moderator.get_full_name() or selected_moderator.username},
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
    with transaction.atomic():
        former_access = list(
            SeriesAccess.objects.filter(series=series).values("user_id", "role")
        )
        meeting_ids = list(Meeting.objects.filter(series=series).values_list("pk", flat=True))
        ArchivedMeetingAccess.objects.bulk_create(
            [
                ArchivedMeetingAccess(meeting_id=meeting_id, user_id=access["user_id"], role=access["role"])
                for meeting_id in meeting_ids
                for access in former_access
            ],
            ignore_conflicts=True,
        )
        # Keep meeting protocols in the archive, but archive every topic
        # belonging to the deleted series as a standalone archived topic.
        topics = Topic.objects.filter(series=series)
        archived_topic_count = topics.count()
        newly_archived_topics = topics.exclude(status="archived")
        newly_archived_topics.update(
            archive_previous_status=models.F("status"),
            status="archived",
            archived_at=timezone.localdate(),
            series=None,
        )
        topics.filter(status="archived").update(series=None)
        Meeting.objects.filter(series=series).update(archived_series_name=name, series=None)
        AuditEvent.objects.create(
            actor=request.user,
            scope=AuditEvent.SCOPE_SYSTEM,
            action="deleted",
            summary=f"Besprechungsreihe „{name}“ gelöscht",
            changes={
                "Bezeichnung": {"vorher": name},
                "Archivierte Besprechungstermine": {"vorher": len(meeting_ids)},
                "Archivierte Themen": {"vorher": archived_topic_count},
                "Ehemalige Mitglieder mit Lesezugriff": {"vorher": len(former_access) if meeting_ids else 0},
            },
        )
        record_event(
            actor=request.user, action="deleted",
            summary=f"Besprechungsreihe „{name}“ gelöscht",
            series=series,
            changes={
                "Archivierte Besprechungstermine": len(meeting_ids),
                "Archivierte Themen": archived_topic_count,
                "Ehemalige Mitglieder mit Lesezugriff": len(former_access) if meeting_ids else 0,
            },
        )
        series.delete()
    messages.success(
        request,
        f"Die Besprechungsreihe „{name}“ wurde gelöscht. "
        "Die Besprechungstermine und Protokolle bleiben zunächst im Archiv erhalten; ihre Protokoll-Snapshots unterliegen der Aufbewahrungsfrist. Alle zugehörigen Themen wurden archiviert."
    )
    return redirect("series_admin" if is_moderator(request.user) else "dashboard")


@login_required
@moderator_required
def series_delete_future(request, pk):
    if request.method != "POST":
        return HttpResponseForbidden()
    series = get_object_or_404(accessible_series(request.user), pk=pk)
    today = timezone.localdate()
    with transaction.atomic():
        future_meetings = Meeting.objects.filter(series=series, date__gte=today)
        deleted_count = future_meetings.count()
        future_meetings.delete()
        # Topics without any remaining agenda entry are no longer active work
        # and are moved to the archive instead of being left orphaned.
        orphaned_topics = Topic.objects.filter(
            series=series, agenda_items__isnull=True
        ).exclude(status="archived")
        orphaned_count = orphaned_topics.count()
        orphaned_topics.update(archive_previous_status=models.F("status"), status="archived", series=None)
        record_event(
            actor=request.user, action="updated",
            summary=f"Zukünftige Termine der Besprechungsreihe „{series.name}“ gelöscht",
            series=series,
            changes={
                "Gelöschte zukünftige Termine": deleted_count,
                "Zusätzlich archivierte Themen ohne verbleibende Tagesordnungspunkte": orphaned_count,
            },
        )
    messages.success(
        request,
        f"{deleted_count} zukünftige Termine der Besprechungsreihe „{series.name}“ wurden gelöscht. "
        "Die dazugehörigen Tagesordnungspunkte dieser Termine wurden ebenfalls entfernt."
    )
    return redirect(f"{reverse('series_admin')}?expanded={series.pk}#series-{series.pk}")

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
    auditor_access = is_auditor(request.user)
    # Series-specific history requires an explicit moderator assignment,
    # including for accounts that also have the global Admin role.
    series = (
        MeetingSeries.objects.none() if auditor_access else
        MeetingSeries.objects.filter(
            user_access__user=request.user,
            user_access__role=SeriesAccess.ROLE_MODERATOR,
        ).distinct().order_by("name")
    )
    has_history_permission = admin_access or auditor_access or series.exists()
    topics = (
        Topic.objects.none() if auditor_access
        else Topic.objects.filter(series__in=series).order_by("title")
    )
    events = AuditEvent.objects.none()
    topic_id = request.GET.get("topic", "")
    selected_series = request.GET.get("series", "")
    selected_action = request.GET.get("action", "")

    if auditor_access:
        events = AuditEvent.objects.filter(
            scope=AuditEvent.SCOPE_SYSTEM
        ).select_related("actor")
        topic_id = ""
        selected_series = ""
    elif admin_access:
        events = AuditEvent.objects.filter(
            Q(scope=AuditEvent.SCOPE_SYSTEM)
            | (
                Q(scope=AuditEvent.SCOPE_SERIES)
                & (
                    Q(series__in=series)
                    | (Q(series__isnull=True) & (
                        Q(topic__series__in=series)
                        | (Q(topic__series__isnull=True) & Q(meeting__series__in=series))
                    ))
                )
            )
        ).select_related("actor", "topic", "meeting", "meeting__series", "series")
    elif has_history_permission:
        events = AuditEvent.objects.filter(
            scope=AuditEvent.SCOPE_SERIES
        ).select_related("actor", "topic", "meeting", "meeting__series", "series").filter(
            Q(series__in=series)
            | (Q(series__isnull=True) & (
                Q(topic__series__in=series)
                | (Q(topic__series__isnull=True) & Q(meeting__series__in=series))
            ))
        )
    else:
        topic_id = ""
        selected_series = ""
        selected_action = ""

    if selected_series.isdigit() and series.filter(pk=int(selected_series)).exists():
        events = events.filter(
            scope=AuditEvent.SCOPE_SERIES
        ).filter(
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

    valid_actions = {value for value, label in AuditEvent.ACTIONS}
    if selected_action in valid_actions:
        events = events.filter(action=selected_action)
    else:
        selected_action = ""

    paginator = Paginator(events.order_by("-created_at", "-pk"), 50)
    events_page = paginator.get_page(request.GET.get("page"))
    return render(request, "meetings/audit_history.html", {
        "events": events_page,
        "page_range": paginator.get_elided_page_range(number=events_page.number, on_each_side=2, on_ends=1),
        "selected_topic": topic_id,
        "topics": topics, "series": series, "selected_series": selected_series,
        "actions": AuditEvent.ACTIONS, "selected_action": selected_action,
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
            before = {
                "Vorname": request.user.first_name,
                "Nachname": request.user.last_name,
                "E-Mail": request.user.email,
                "Organisationskennzeichen": getattr(getattr(request.user, "meeting_profile", None), "short_description", ""),
            }
            profile_form.save()
            after = {
                "Vorname": request.user.first_name,
                "Nachname": request.user.last_name,
                "E-Mail": request.user.email,
                "Organisationskennzeichen": getattr(getattr(request.user, "meeting_profile", None), "short_description", ""),
            }
            changes = {label: {"vorher": before[label], "nachher": value} for label, value in after.items() if before[label] != value}
            if changes:
                AuditEvent.objects.create(
                    actor=request.user, scope=AuditEvent.SCOPE_SYSTEM, action="updated",
                    summary=f"Eigenes Benutzerprofil von „{request.user.get_full_name() or request.user.username}“ geändert",
                    changes=changes,
                )
            messages.success(request, "Deine persönlichen Daten wurden gespeichert.")
            return redirect("user_overview")
        messages.error(request, "Bitte prüfe deine persönlichen Angaben.")
    else:
        profile_form = PersonalProfileForm(user=request.user)
        password_form = PasswordChangeForm(request.user)

    if request.method == "POST" and request.POST.get("form_type") == "password":
        if password_form.is_valid():
            user = password_form.save()
            AuditEvent.objects.create(
                actor=request.user, scope=AuditEvent.SCOPE_SYSTEM, action="updated",
                summary=f"Passwort von „{user.get_full_name() or user.username}“ geändert",
                changes={"Passwort": {"nachher": "Geändert (Passwortwert wird nicht protokolliert)"}},
            )
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
            "role_label": role_labels.get(assignment.role, assignment.role) if assignment else "Keine Berechtigung",
            "role_value": assignment.role if assignment else "",
            "pending_request": pending if pending and pending.status == SeriesAccessRequest.STATUS_PENDING else None,
            "latest_request": pending,
            "can_request": not (pending and pending.status == SeriesAccessRequest.STATUS_PENDING),
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
import re
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
BRANCH_NAME_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]{0,119}$")
TESTING_MODE_FILE = Path("/var/lib/meeting-manager-updater/testing-mode")


class _UnixSocketHTTPConnection(http.client.HTTPConnection):
    def __init__(self, socket_path, timeout=3):
        super().__init__("localhost", timeout=timeout)
        self.socket_path = socket_path

    def connect(self):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.settimeout(self.timeout)
        self.sock.connect(self.socket_path)


def _updater_request(path, method="GET", payload=None):
    connection = _UnixSocketHTTPConnection(UPDATE_SOCKET, timeout=20)
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {"Content-Type": "application/json"} if body is not None else {}
    try:
        connection.request(method, path, body=body, headers=headers)
        response = connection.getresponse()
        data = json.loads(response.read().decode("utf-8"))
        return response.status, data
    finally:
        connection.close()


def _debian_testing_mode_enabled():
    return os.path.isfile(TESTING_MODE_FILE)


def testing_mode_context(request):
    """Expose the active Debian testing mode to every rendered page."""
    return {"testing_mode": _debian_testing_mode_enabled()}


def _available_update_branches():
    """Return branches supported by this deployment and its active update mode."""
    try:
        if os.path.exists(UPDATE_SOCKET):
            # Docker keeps its existing dynamic branch behavior; -testing is Debian-only.
            code, data = _updater_request("/branches")
            if code == 404:
                branches = ["beta", "main"]
            elif code != 200:
                raise RuntimeError(data.get("error", "Branches konnten nicht geladen werden."))
            else:
                branches = data.get("branches", [])
        elif os.path.isfile(DEBIAN_UPDATE_COMMAND):
            result = subprocess.run(
                ["/usr/bin/git", "-c", "safe.directory=/opt/meeting-manager", "-C",
                 "/opt/meeting-manager", "ls-remote", "--heads", "origin"],
                text=True, capture_output=True, timeout=15, check=True,
            )
            branches = [
                line.split("\t", 1)[1][len("refs/heads/"):]
                for line in result.stdout.splitlines()
                if "\trefs/heads/" in line
            ]
            if not _debian_testing_mode_enabled():
                branches = [name for name in branches if name in {"main", "beta"}]
        else:
            return []
        return sorted({
            name for name in branches
            if isinstance(name, str) and BRANCH_NAME_PATTERN.fullmatch(name)
            and ".." not in name and not name.endswith(("/", "."))
        }, key=str.casefold)
    except (OSError, ValueError, http.client.HTTPException, subprocess.SubprocessError, RuntimeError):
        return []


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
    is_debian_deployment = info["deployment_type"] == "Debian / systemd"
    testing_mode = is_debian_deployment and _debian_testing_mode_enabled()
    available_branches = _available_update_branches()
    if request.method == "POST":
        if request.POST.get("action") == "disable-testing":
            if not testing_mode:
                messages.error(request, "Der Testing-Modus ist nicht aktiviert.")
                return redirect("deployment_updates")
            status = _read_update_status()
            if status.get("status") == "running":
                messages.warning(request, "Der Testing-Modus kann während eines laufenden Updates nicht deaktiviert werden.")
                return redirect("deployment_updates")
            try:
                disabled = subprocess.run(
                    ["sudo", "-n", DEBIAN_UPDATE_COMMAND, "--disable-testing"],
                    stdin=subprocess.DEVNULL, capture_output=True, text=True,
                    timeout=10, check=False,
                )
                if disabled.returncode != 0:
                    raise RuntimeError(disabled.stderr.strip() or "Der Testing-Modus konnte nicht deaktiviert werden.")
                messages.success(request, "Testing-Modus wurde deaktiviert. Es stehen wieder nur main und beta zur Verfügung.")
            except (OSError, RuntimeError, subprocess.SubprocessError) as exc:
                messages.error(request, f"Testing-Modus konnte nicht deaktiviert werden: {exc}")
            return redirect("deployment_updates")

        branch = request.POST.get("branch", "")
        if branch not in available_branches:
            messages.error(request, "Bitte einen aktuell verfügbaren Branch auswählen.")
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

    if info["update_available"] and not available_branches:
        info["update_available"] = False
        info["availability_message"] = "Die verfügbaren Branches konnten nicht vom Repository geladen werden. Bitte Verbindung und Updater prüfen."
    return render(request, "meetings/deployment_updates.html", {
        **info,
        "available_branches": available_branches,
        "testing_mode": testing_mode,
        "is_debian_deployment": is_debian_deployment,
        "update_status": update_status,
    })
