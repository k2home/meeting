import logging

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from meetings.models import (
    AgendaItem, AuditEvent, Meeting, RetainedAgendaEntry, Topic,
    TopicAttachment, TopicSnapshot,
)
from meetings.retention import (
    effective_retention_years, retention_expiry_date, topic_deletion_date,
)
from meetings.user_display import user_display_name

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Löscht abgelaufene Themen sowie Besprechungstermine und Protokolle nach der globalen Aufbewahrungsfrist."

    def handle(self, *args, **options):
        today = timezone.localdate()
        deleted_topics = 0
        deleted_meetings = 0
        deleted_snapshots = 0

        # A topic owns its agenda history. Delete it only when its individual
        # retention period has expired; related retained agenda entries cascade.
        archived_topic_ids = list(
            Topic.objects.filter(status="archived").order_by("pk").values_list("pk", flat=True)
        )
        for topic_id in archived_topic_ids:
            with transaction.atomic():
                try:
                    locked_topic = Topic.objects.select_for_update().get(pk=topic_id)
                except Topic.DoesNotExist:
                    continue
                expiry = topic_deletion_date(locked_topic)
                if not expiry or expiry >= today:
                    continue

                meeting_ids = set(
                    AgendaItem.objects.filter(topic=locked_topic).values_list("meeting_id", flat=True)
                )
                meeting_ids.update(
                    TopicSnapshot.objects.filter(topic_id=locked_topic.pk).values_list("meeting_id", flat=True)
                )
                for meeting_id in meeting_ids:
                    self._redact_protocol_audit(meeting_id, locked_topic.pk)

                attachments = list(TopicAttachment.objects.filter(topic=locked_topic))
                stored_files = [
                    (attachment.uploaded_file.storage, attachment.uploaded_file.name)
                    for attachment in attachments if attachment.uploaded_file
                ]
                deleted_snapshots += TopicSnapshot.objects.filter(topic_id=locked_topic.pk).count()
                TopicSnapshot.objects.filter(topic_id=locked_topic.pk).delete()
                AgendaItem.objects.filter(topic=locked_topic).delete()
                AuditEvent.objects.filter(topic=locked_topic).delete()
                locked_topic.delete()
                for storage, name in stored_files:
                    transaction.on_commit(
                        lambda storage=storage, name=name: self._delete_file(storage, name)
                    )
            deleted_topics += 1

        # A meeting's protocol retention is independent of every topic's
        # individual retention. Preserve only the topic-owned agenda text;
        # protocol snapshots and their audit copies expire with the meeting.
        organization_years = effective_retention_years()
        meeting_ids = list(Meeting.objects.order_by("pk").values_list("pk", flat=True))
        for meeting_id in meeting_ids:
            with transaction.atomic():
                try:
                    locked_meeting = Meeting.objects.select_for_update().select_related("series").get(pk=meeting_id)
                except Meeting.DoesNotExist:
                    continue
                was_reopened = AuditEvent.objects.filter(
                    meeting_id=locked_meeting.pk, action="reopened"
                ).exists()
                if not locked_meeting.finalized_at and not was_reopened:
                    continue
                expiry = retention_expiry_date(locked_meeting.date, organization_years)
                if not expiry or expiry >= today:
                    continue

                series_name = (
                    locked_meeting.series.name if locked_meeting.series_id
                    else locked_meeting.archived_series_name or "Gelöschte Besprechungsreihe"
                )
                agenda_items = list(
                    AgendaItem.objects.filter(meeting=locked_meeting)
                    .select_related("topic", "assigned_to")
                )
                topic_ids = {item.topic_id for item in agenda_items}
                topic_ids.update(
                    TopicSnapshot.objects.filter(meeting=locked_meeting)
                    .values_list("topic_id", flat=True)
                )
                # Reopened protocols may survive only as JSON copies in audit
                # events and no longer have a live agenda item or snapshot.
                for event in AuditEvent.objects.filter(meeting=locked_meeting).only("topic_id", "changes"):
                    if event.topic_id:
                        topic_ids.add(event.topic_id)
                    changes = event.changes or {}
                    saved = changes.get("Gesicherter Protokollstand")
                    if isinstance(saved, list):
                        topic_ids.update(
                            entry["topic_id"] for entry in saved
                            if isinstance(entry, dict) and entry.get("topic_id")
                        )
                    correction = changes.get("Protokollkorrektur")
                    if isinstance(correction, dict):
                        for side in ("vorher", "nachher"):
                            entry = correction.get(side) or {}
                            if isinstance(entry, dict) and entry.get("topic_id"):
                                topic_ids.add(entry["topic_id"])
                for topic_id in topic_ids:
                    self._redact_protocol_audit(locked_meeting.pk, topic_id)

                for item in agenda_items:
                    RetainedAgendaEntry.objects.update_or_create(
                        topic_id=item.topic_id,
                        original_meeting_id=locked_meeting.pk,
                        defaults={
                            "meeting_date": locked_meeting.date,
                            "series_name": series_name,
                            "working_text": item.working_text,
                            "status": item.status,
                            "responsible_name": (
                                user_display_name(item.assigned_to, include_short_description=True)
                                if item.assigned_to_id else (
                                    user_display_name(item.topic.assigned_to, include_short_description=True)
                                    if item.topic.assigned_to_id else ""
                                )
                            ),
                            "position": item.position,
                        },
                    )

                deleted_snapshots += TopicSnapshot.objects.filter(meeting=locked_meeting).count()
                # AuditEvent.meeting uses SET_NULL: non-protocol audit metadata
                # remains available without keeping the meeting itself.
                locked_meeting.delete()
            deleted_meetings += 1

        self.stdout.write(self.style.SUCCESS(
            f"Aufbewahrungsprüfung abgeschlossen: {deleted_topics} Themen, "
            f"{deleted_meetings} Besprechungstermine und {deleted_snapshots} Protokollstände gelöscht."
        ))

    @staticmethod
    def _redact_protocol_audit(meeting_id, topic_id):
        events = AuditEvent.objects.filter(meeting_id=meeting_id).only("pk", "topic_id", "changes")
        for event in events.iterator():
            changes = event.changes or {}
            modified = False
            if event.topic_id == topic_id:
                # Agenda edit history can also contain copies of protocol text.
                for key in ("Text", "Besprechungstext"):
                    if key in changes:
                        changes.pop(key, None)
                        modified = True
            saved = changes.get("Gesicherter Protokollstand")
            if isinstance(saved, list):
                filtered = [
                    entry for entry in saved
                    if not isinstance(entry, dict) or entry.get("topic_id") != topic_id
                ]
                if len(filtered) != len(saved):
                    if filtered:
                        changes["Gesicherter Protokollstand"] = filtered
                    else:
                        changes.pop("Gesicherter Protokollstand", None)
                    modified = True
            correction = changes.get("Protokollkorrektur")
            if isinstance(correction, dict):
                before = correction.get("vorher") or {}
                after = correction.get("nachher") or {}
                if before.get("topic_id") == topic_id or after.get("topic_id") == topic_id:
                    correction.pop("vorher", None)
                    correction.pop("nachher", None)
                    modified = True
            if modified:
                event.changes = changes
                event.save(update_fields=["changes"])

    @staticmethod
    def _delete_file(storage, name):
        try:
            storage.delete(name)
        except Exception:
            logger.exception(
                "Abgelaufene Themenanlage konnte nicht aus dem Dateispeicher gelöscht werden: %s",
                name,
            )
