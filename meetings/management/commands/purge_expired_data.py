import logging

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from meetings.models import AgendaItem, AuditEvent, Topic, TopicAttachment, TopicSnapshot
from meetings.retention import protocol_deletion_date, topic_deletion_date

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Löscht abgelaufene archivierte Themen und gesicherte Protokollstände."

    def handle(self, *args, **options):
        today = timezone.localdate()
        deleted_topics = 0
        deleted_snapshots = 0

        archived_topics = Topic.objects.filter(status="archived").order_by("pk")
        for topic in archived_topics.iterator():
            expiry = topic_deletion_date(topic)
            if not expiry or expiry >= today:
                continue
            with transaction.atomic():
                locked_topic = Topic.objects.select_for_update().get(pk=topic.pk)
                expiry = topic_deletion_date(locked_topic)
                if not expiry or expiry >= today:
                    continue
                agenda_items = list(AgendaItem.objects.filter(topic=locked_topic).values("meeting_id"))
                snapshot_meeting_ids = set(
                    TopicSnapshot.objects.filter(topic_id=locked_topic.pk).values_list("meeting_id", flat=True)
                )
                for meeting_id in snapshot_meeting_ids | {
                    item["meeting_id"] for item in agenda_items
                }:
                    self._redact_protocol_audit(meeting_id, locked_topic.pk)

                attachments = list(TopicAttachment.objects.filter(topic=locked_topic))
                stored_files = [
                    (attachment.uploaded_file.storage, attachment.uploaded_file.name)
                    for attachment in attachments if attachment.uploaded_file
                ]
                TopicSnapshot.objects.filter(topic_id=locked_topic.pk).delete()
                # AgendaItem protects Topic from accidental deletion; remove its
                # rows explicitly while retaining no content after topic expiry.
                AgendaItem.objects.filter(topic=locked_topic).delete()
                AuditEvent.objects.filter(topic=locked_topic).delete()
                locked_topic.delete()
                for storage, name in stored_files:
                    transaction.on_commit(
                        lambda storage=storage, name=name: self._delete_file(storage, name)
                    )
            deleted_topics += 1

        # Active topics retain their agenda text. Only immutable snapshots and
        # copies of those snapshots in reopen/correction audit records expire.
        active_topics = {
            topic.pk: topic
            for topic in Topic.objects.exclude(status="archived").only(
                "id", "status", "retention_years"
            )
        }
        expired_keys = set()
        snapshots = TopicSnapshot.objects.filter(
            meeting__finalized_at__isnull=False
        ).select_related("meeting").order_by("pk")
        for snapshot in snapshots.iterator():
            topic = active_topics.get(snapshot.topic_id)
            if topic is None:
                continue
            expiry = protocol_deletion_date(snapshot.meeting, topic)
            if expiry and expiry < today:
                expired_keys.add((snapshot.meeting_id, snapshot.topic_id))

        # A reopened meeting moves its former snapshot into an audit event.
        # Apply the same meeting-date retention to those retained copies.
        reopen_events = AuditEvent.objects.filter(
            action="reopened", meeting__isnull=False
        ).select_related("meeting").order_by("pk")
        for event in reopen_events.iterator():
            saved_snapshots = (event.changes or {}).get("Gesicherter Protokollstand")
            if not isinstance(saved_snapshots, list):
                continue
            for saved in saved_snapshots:
                topic_id = saved.get("topic_id") if isinstance(saved, dict) else None
                topic = active_topics.get(topic_id)
                if topic and protocol_deletion_date(event.meeting, topic) < today:
                    expired_keys.add((event.meeting_id, topic_id))

        for meeting_id, topic_id in expired_keys:
            self._redact_protocol_audit(meeting_id, topic_id)

        if expired_keys:
            snapshot_filter = [
                (meeting_id, topic_id) for meeting_id, topic_id in expired_keys
            ]
            for meeting_id, topic_id in snapshot_filter:
                deleted_snapshots += TopicSnapshot.objects.filter(
                    meeting_id=meeting_id, topic_id=topic_id
                ).delete()[0]

        self.stdout.write(self.style.SUCCESS(
            f"Aufbewahrungsprüfung abgeschlossen: {deleted_topics} Themen und "
            f"{deleted_snapshots} Protokollstände gelöscht."
        ))

    @staticmethod
    def _redact_protocol_audit(meeting_id, topic_id):
        events = AuditEvent.objects.filter(meeting_id=meeting_id).only("pk", "changes")
        for event in events.iterator():
            changes = event.changes or {}
            modified = False
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
