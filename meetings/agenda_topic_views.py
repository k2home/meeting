from django import forms
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import formats, timezone

from .access import accessible_meetings, accessible_series, accessible_topics, auditor_readonly, is_admin, is_auditor, is_moderator, is_reader
from .audit import record_event
from .forms import UserDisplayModelChoiceField
from .models import AgendaItem, Meeting, MeetingSeries, SeriesAccess, Topic, TopicSnapshot
from .user_display import user_display_name


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


class NewTopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ["title", "series"]


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
    if topic.series_id is None or not is_moderator(request.user, topic.series):
        return HttpResponseForbidden("Nur Moderator*innen und Admins der Besprechungsreihe dürfen Themen archivieren oder wieder öffnen.")
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
            has_future_agenda = topic.agenda_items.filter(
                meeting__finalized_at__isnull=True,
            ).exists()
            if has_future_agenda:
                messages.error(
                    request,
                    "Das Thema kann noch nicht archiviert werden, solange es auf einer zukünftigen oder offenen Tagesordnung steht. Entferne zuerst die geplanten Tagesordnungspunkte.",
                )
                return redirect("topic_edit", pk=topic.pk)
            previous_status = topic.status
            topic.archive_previous_status = previous_status
            topic.status = "archived"
            topic.save(update_fields=["status", "archive_previous_status", "updated_at"])
            record_event(
                actor=request.user, action="archived",
                summary=f"Thema „{topic.title}“ archiviert",
                topic=topic,
                changes={"Themenstatus": {"vorher": dict(Topic.STATUS).get(previous_status, previous_status), "nachher": "Archiviert"}},
            )
            messages.success(request, f"„{topic.title}“ wurde archiviert.")
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
        "title", "assigned_to_id"
    ).get()
    form = TopicTitleForm(request.POST or None, instance=topic)
    if reader:
        form.fields["title"].disabled = True
        form.fields["assigned_to"].disabled = True
    if request.method == "POST":
        if reader:
            return HttpResponseForbidden("Leser*innen haben ausschließlich Leserechte.")
        if form.is_valid():
            # Capture the persisted values before ModelForm.save() mutates the
            # instance. Keep the write and its audit record in the same
            # transaction so an audit failure cannot leave an unaudited edit.
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
        )
    }
    for item in items:
        snapshot = snapshots.get(item.meeting_id)
        item.display_text = snapshot.text if snapshot else item.working_text
        item.snapshot_exists = snapshot is not None

    writable_series = accessible_series(request.user).exclude(user_access__role=SeriesAccess.ROLE_READER)
    return render(request, "meetings/topic_form.html", {
        "form": form,
        "topic": topic,
        "can_archive_topic": topic.series_id is not None and is_moderator(request.user, topic.series),
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
    new_text = request.POST.get("working_text", "")
    old_text = item.working_text
    old_assignee = item.assigned_to_id
    item.working_text = new_text
    item.assigned_to = assignee
    if old_text != new_text or old_assignee != item.assigned_to_id:
        item.save(update_fields=["working_text", "assigned_to"])
        changes = {}
        if old_text != new_text:
            changes["Besprechungstext"] = {"vorher": old_text, "nachher": new_text}
        if old_assignee != item.assigned_to_id:
            changes["Zuständigkeit"] = {
                "vorher": str(old_assignee) if old_assignee else None,
                "nachher": str(item.assigned_to_id) if item.assigned_to_id else None,
            }
        record_event(
            actor=request.user, action="agenda_edited",
            summary=f"Agenda-Punkt „{item.topic.title}“ am {formats.date_format(item.meeting.date, 'DATE_FORMAT')} geändert",
            topic=item.topic, meeting=item.meeting, changes=changes,
        )
        messages.success(request, "Tagesordnungstext gespeichert.")
    else:
        messages.info(request, "Es wurden keine Änderungen vorgenommen.")
    return redirect("topic_edit", pk=pk)
