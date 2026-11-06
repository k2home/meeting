from django.conf import settings
from django.db import models
from django.utils import timezone

class MeetingSeries(models.Model):
    name = models.CharField("Bezeichnung", max_length=160, unique=True)
    description = models.TextField("Beschreibung", blank=True)
    active = models.BooleanField("Aktiv", default=True)
    recurrence = models.CharField("Wiederholung", max_length=12, choices=[("weekly", "Wöchentlich"), ("biweekly", "14-tägig"), ("monthly", "Monatlich")], default="monthly")
    weekday = models.PositiveSmallIntegerField("Wochentag (0=Mo)", default=0)
    start_date = models.DateField("Startdatum", default=timezone.localdate)
    end_date = models.DateField("Enddatum", null=True, blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Besprechungsreihe"
        verbose_name_plural = "Besprechungsreihen"

    def __str__(self):
        return self.name

class Meeting(models.Model):
    series = models.ForeignKey(MeetingSeries, on_delete=models.CASCADE, related_name="meetings")
    date = models.DateField("Termin")
    title = models.CharField("Titel", max_length=180, blank=True)
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="meeting_participations", verbose_name="Teilnehmer")
    finalized_at = models.DateTimeField("Abgeschlossen am", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["date"]
        constraints = [models.UniqueConstraint(fields=["series", "date"], name="unique_series_meeting_date")]
        verbose_name = "Besprechung"
        verbose_name_plural = "Besprechungen"

    def __str__(self):
        return self.title or f"{self.series} – {self.date:%d.%m.%Y}"

class Topic(models.Model):
    STATUS = [("open", "Offen"), ("done", "Erledigt"), ("archived", "Archiviert")]
    title = models.CharField("Thema", max_length=240)
    description = models.TextField("Aktueller Stand", blank=True)
    due_date = models.DateField("Fällig am", null=True, blank=True)
    status = models.CharField("Status", max_length=12, choices=STATUS, default="open")
    series = models.ForeignKey(MeetingSeries, on_delete=models.SET_NULL, null=True, blank=True, related_name="topics")
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name="assigned_meeting_topics", verbose_name="Verantwortlich")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["due_date", "title"]
        verbose_name = "Thema"
        verbose_name_plural = "Themen"

    def __str__(self):
        return self.title

class TopicTransferHistory(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="transfer_history")
    from_series = models.ForeignKey(MeetingSeries, on_delete=models.SET_NULL, null=True, blank=True, related_name="outgoing_topic_transfers")
    to_series = models.ForeignKey(MeetingSeries, on_delete=models.SET_NULL, null=True, blank=True, related_name="incoming_topic_transfers")
    transferred_at = models.DateTimeField(auto_now_add=True)
    transferred_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    note = models.CharField("Notiz", max_length=500, blank=True)

    class Meta:
        ordering = ["-transferred_at"]
        verbose_name = "Themenübertragung"
        verbose_name_plural = "Themenübertragungen"

class AgendaItem(models.Model):
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name="agenda_items")
    topic = models.ForeignKey(Topic, on_delete=models.PROTECT, related_name="agenda_items")
    working_text = models.TextField("Text für dieses Protokoll", blank=True)
    position = models.PositiveIntegerField(default=0)
    carried_forward = models.BooleanField(default=False)

    class Meta:
        ordering = ["position", "id"]
        constraints = [models.UniqueConstraint(fields=["meeting", "topic"], name="unique_topic_per_meeting")]

class TopicSnapshot(models.Model):
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name="snapshots")
    topic_title = models.CharField(max_length=240)
    text = models.TextField(blank=True)
    status = models.CharField(max_length=12)
    topic_id = models.PositiveBigIntegerField()

    class Meta:
        ordering = ["id"]

class TopicAttachment(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="attachments")
    label = models.CharField("Bezeichnung", max_length=180)
    uploaded_file = models.FileField("Datei-Upload", upload_to="topic-files/%Y/%m/", blank=True)
    network_path = models.CharField("Netzwerkpfad / Link", max_length=1000, blank=True)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.label


class AuditEvent(models.Model):
    """Unveränderlicher Eintrag für wichtige Änderungen in der Anwendung."""
    ACTIONS = [
        ("created", "Angelegt"),
        ("updated", "Geändert"),
        ("archived", "Archiviert"),
        ("reopened", "Wieder geöffnet"),
        ("transferred", "Übertragen"),
        ("attachment_added", "Anlage hinzugefügt"),
        ("agenda_edited", "Agendatext geändert"),
        ("finalized", "Besprechung abgeschlossen"),
        ("comment_added", "Kommentar hinzugefügt"),
    ]
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True, blank=True, related_name="audit_events")
    meeting = models.ForeignKey(Meeting, on_delete=models.SET_NULL, null=True, blank=True, related_name="audit_events")
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="meeting_audit_events")
    action = models.CharField("Aktion", max_length=24, choices=ACTIONS)
    summary = models.CharField("Beschreibung", max_length=500)
    changes = models.JSONField("Änderungen", default=dict, blank=True)
    created_at = models.DateTimeField("Zeitpunkt", auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-pk"]
        verbose_name = "Änderungsverlauf"
        verbose_name_plural = "Änderungsverläufe"

    def __str__(self):
        return f"{self.get_action_display()}: {self.summary}"


class TopicComment(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                               related_name="meeting_topic_comments")
    body = models.TextField("Kommentar", max_length=5000)
    created_at = models.DateTimeField("Erstellt am", auto_now_add=True)

    class Meta:
        ordering = ["created_at", "pk"]
        verbose_name = "Themenkommentar"
        verbose_name_plural = "Themenkommentare"

    def __str__(self):
        return f"Kommentar zu {self.topic}"
