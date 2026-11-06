from django.conf import settings
from django.db import models
from django.utils import timezone

class MeetingSeries(models.Model):
    name = models.CharField("Bezeichnung", max_length=160, unique=True)
    description = models.TextField("Beschreibung", blank=True)
    active = models.BooleanField("Aktiv", default=True)
    recurrence = models.CharField("Wiederholung", max_length=12, choices=[("weekly","Wöchentlich"),("biweekly","14-tägig"),("monthly","Monatlich")], default="monthly")
    weekday = models.PositiveSmallIntegerField("Wochentag (0=Mo)", default=0)
    start_date = models.DateField("Startdatum", default=timezone.localdate)
    end_date = models.DateField("Enddatum", null=True, blank=True)
    class Meta:
        ordering = ["name"]
        verbose_name = "Besprechungsreihe"
        verbose_name_plural = "Besprechungsreihen"
    def __str__(self): return self.name

class Meeting(models.Model):
    series = models.ForeignKey(MeetingSeries, on_delete=models.CASCADE, related_name="meetings")
    date = models.DateField("Termin")
    title = models.CharField("Titel", max_length=180, blank=True)
    finalized_at = models.DateTimeField("Abgeschlossen am", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ["date"]
        constraints = [models.UniqueConstraint(fields=["series","date"], name="unique_series_meeting_date")]
        verbose_name = "Besprechung"
        verbose_name_plural = "Besprechungen"
    def __str__(self): return self.title or f"{self.series} – {self.date:%d.%m.%Y}"

class Topic(models.Model):
    STATUS = [("open","Offen"),("done","Erledigt"),("archived","Archiviert")]
    title = models.CharField("Thema", max_length=240)
    description = models.TextField("Aktueller Stand", blank=True)
    due_date = models.DateField("Fällig am", null=True, blank=True)
    status = models.CharField("Status", max_length=12, choices=STATUS, default="open")
    series = models.ForeignKey(MeetingSeries, on_delete=models.SET_NULL, null=True, blank=True, related_name="topics")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ["due_date", "title"]
        verbose_name = "Thema"
        verbose_name_plural = "Themen"
    def __str__(self): return self.title

class AgendaItem(models.Model):
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name="agenda_items")
    topic = models.ForeignKey(Topic, on_delete=models.PROTECT, related_name="agenda_items")
    working_text = models.TextField("Text für dieses Protokoll", blank=True)
    position = models.PositiveIntegerField(default=0)
    carried_forward = models.BooleanField(default=False)
    class Meta:
        ordering = ["position", "id"]
        constraints = [models.UniqueConstraint(fields=["meeting","topic"], name="unique_topic_per_meeting")]

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
    def __str__(self): return self.label
