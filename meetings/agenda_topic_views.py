from django import forms
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .access import accessible_meetings, accessible_series, accessible_topics, is_admin, is_reader
from .audit import record_event
from .models import AgendaItem, Meeting, SeriesAccess, Topic, TopicSnapshot


class TopicTitleForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ["title"]


class NewTopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ["title", "series"]


@login_required
def topic_new(request):
    writable_series = accessible_series(request.user)
    if not is_admin(request.user):
        writable_series = writable_series.exclude(user_access__role=SeriesAccess.ROLE_READER)
        if not writable_series.exists():
            return HttpResponseForbidden("Für diese Funktion ist eine Teilnehmer- oder Moderatorrolle erforderlich.")
    form = NewTopicForm(request.POST or None)
    form.fields["series"].queryset = writable_series.filter(active=True)
    form.fields["series"].required = not is_admin(request.user)
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
            messages.success(request, f"„{topic.title}“ wurde auf die Tagesordnung am {meeting.date:%d.%m.%Y} gesetzt.")
            return redirect("topic_edit", pk=topic.pk)
    return render(request, "meetings/topic_form.html", {
        "form": form, "available_meetings": meetings,
        "is_reader": not writable_series.exists(),
    })


@login_required
def topic_detail(request, pk):
    topic = get_object_or_404(accessible_topics(request.user), pk=pk)
    reader = is_reader(request.user, topic.series)
    form = TopicTitleForm(request.POST or None, instance=topic)
    if reader:
        form.fields["title"].disabled = True
    if request.method == "POST":
        if reader:
            return HttpResponseForbidden("Leser*innen haben ausschließlich Leserechte.")
        if form.is_valid():
            old_title = topic.title
            updated = form.save()
            if old_title != updated.title:
                record_event(
                    actor=request.user, action="updated",
                    summary=f"Thema „{updated.title}“ umbenannt",
                    topic=updated,
                    changes={"Titel": {"vorher": old_title, "nachher": updated.title}},
                )
            messages.success(request, "Thementitel gespeichert.")
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

    # Keep legacy free-text data visible after moving the editing workflow to
    # meeting agenda entries. It is not copied over or allowed to overwrite
    # any meeting-specific protocol text.
    legacy_description = (topic.description or "").strip()
    if legacy_description and legacy_description not in [item.display_text.strip() for item in items]:
        legacy_description = legacy_description
    else:
        legacy_description = ""

    writable_series = accessible_series(request.user)
    if not is_admin(request.user):
        writable_series = writable_series.exclude(user_access__role=SeriesAccess.ROLE_READER)
    return render(request, "meetings/topic_form.html", {
        "form": form,
        "topic": topic,
        "is_reader": reader,
        "topic_agenda_items": items,
        "legacy_description": legacy_description,
        "transfer_series": writable_series.filter(active=True).exclude(pk=topic.series_id),
        "assignees": get_user_model().objects.filter(is_active=True).order_by("last_name", "first_name", "username"),
    })


@login_required
def edit_topic_agenda_item(request, pk, item_pk):
    if request.method != "POST":
        return HttpResponseForbidden()
    item = get_object_or_404(
        AgendaItem.objects.select_related("topic", "meeting__series"),
        pk=item_pk, topic_id=pk, meeting__in=accessible_meetings(request.user),
    )
    if is_reader(request.user, item.meeting.series) or item.meeting.finalized_at:
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
            summary=f"Agenda-Punkt „{item.topic.title}“ am {item.meeting.date:%d.%m.%Y} geändert",
            topic=item.topic, meeting=item.meeting, changes=changes,
        )
        messages.success(request, "Tagesordnungstext gespeichert.")
    else:
        messages.info(request, "Es wurden keine Änderungen vorgenommen.")
    return redirect("topic_edit", pk=pk)
