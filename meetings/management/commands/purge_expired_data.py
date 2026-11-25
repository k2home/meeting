import logging

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from meetings.models import AgendaItem, AuditEvent, Topic, TopicAttachment, TopicSnapshot
from meetings.retention import effective_retention_years, protocol_deletion_date, topic_deletion_date

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Löscht abgelaufene archivierte Themen und gesicherte Protokollstände."

    def handle(self, *args, **options):
        today = timezone.localdate()
        deleted_topics = 0
        deleted_snapshots = 0

        archived_topics = Topic.objects.filter(status="archived").select_related("series").order_by("pk")
        for topic in archived_topics.iterator():
            expiry = topic_deletion_date(topic)
            if expiry and expiry < today:
                with transaction.atomic():
                    locked_topic = Topic.objects.select_for_update().get(pk=topic.pk)
                    expiry = topic_deletion_date(locked_topic)
                    if not expiry or expiry >= today:
                        continue
                    attachments = list(TopicAttachment.objects.filter(topic=locked_topic))
                    stored_files = [
                        (attachment.uploaded_file.storage, attachment.uploaded_file.name)
                        for attachment in attachments if attachment.uploaded_file
                    ]
                    TopicSnapshot.objects.filter(topic_id=locked_topic.pk).delete()
                    AgendaItem.objects.filter(topic=locked_topic).delete()
                    AuditEvent.objects.filter(topic=locked_topic).delete()
                    locked_topic.delete()
                    for storage, name in stored_files:
                        transaction.on_commit(
                            lambda storage=storage, name=name: self._delete_file(storage, name)
                        )
                deleted_topics += 1

        # For still-active topics, expire only the immutable snapshots belonging
        # to finalized meetings. AgendaItem.working_text remains the live topic history.
        topics = {
            topic.pk: topic
            for topic in Topic.objects.exclude(status="archived").only(
                "id", "status", "retention_years"
            )
        }
        expired_snapshot_ids = []
        snapshots = TopicSnapshot.objects.filter(
            meeting__finalized_at__isnull=False
        ).select_related("meeting").order_by("pk")
        for snapshot in snapshots.iterator():
            topic = topics.get(snapshot.topic_id)
            if topic is None:
                continue
            expiry = protocol_deletion_date(snapshot.meeting, topic)
            if expiry and expiry < today:
                expired_snapshot_ids.append(snapshot.pk)
        if expired_snapshot_ids:
            deleted_snapshots, _ = TopicSnapshot.objects.filter(
                pk__in=expired_snapshot_ids
            ).delete()

        self.stdout.write(self.style.SUCCESS(
            f"Aufbewahrungsprüfung abgeschlossen: {deleted_topics} Themen und "
            f"{deleted_snapshots} Protokollstände gelöscht."
        ))

    @staticmethod
    def _delete_file(storage, name):
        try:
            storage.delete(name)
        except Exception:
            logger.exception("Abgelaufene Themenanlage konnte nicht aus dem Dateispeicher gelöscht werden: %s", name)
