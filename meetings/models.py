from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone

class MeetingSeries(models.Model):
    name = models.CharField("Bezeichnung", max_length=160, unique=True)
    description = models.TextField("Beschreibung", blank=True)
    active = models.BooleanField("Aktiv", default=True)
    recurrence = models.CharField("Wiederholung", max_length=12, choices=[("weekly", "Wöchentlich"), ("monthly", "Monatlich")], default="monthly")
    recurrence_interval = models.PositiveSmallIntegerField("Wiederholungsintervall", default=1)
    weekday = models.PositiveSmallIntegerField("Wochentag (0=Mo)", default=0)
    start_date = models.DateField("Startdatum", default=timezone.localdate)
    end_date = models.DateField("Enddatum", null=True, blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Besprechungsreihe"
        verbose_name_plural = "Besprechungsreihen"

    @property
    def weekday_label(self):
        return ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"][self.weekday]

    def __str__(self):
        return self.name

class Meeting(models.Model):
    series = models.ForeignKey(MeetingSeries, on_delete=models.SET_NULL, null=True, blank=True, related_name="meetings")
    date = models.DateField("Termin")
    title = models.CharField("Titel", max_length=180, blank=True)
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="meeting_participations", verbose_name="Teilnehmer")
    participants_initialized = models.BooleanField("Teilnehmer-Voreinstellung angewendet", default=False)
    finalized_at = models.DateTimeField("Abgeschlossen am", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["date"]
        constraints = [models.UniqueConstraint(fields=["series", "date"], name="unique_series_meeting_date")]
        verbose_name = "Besprechung"
        verbose_name_plural = "Besprechungen"

    def __str__(self):
        return self.title or f"{self.series or 'Gelöschte Besprechungsreihe'} – {self.date:%d.%m.%Y}"

class Topic(models.Model):
    STATUS = [("open", "Offen"), ("in_progress", "In Arbeit"), ("done", "Erledigt"), ("archived", "Archiviert")]
    title = models.CharField("Thema", max_length=240)
    status = models.CharField("Status", max_length=12, choices=STATUS, default="open")
    series = models.ForeignKey(MeetingSeries, on_delete=models.SET_NULL, null=True, blank=True, related_name="topics")
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name="assigned_meeting_topics", verbose_name="Verantwortlich")
    completed_at = models.DateField("Abschlussdatum", null=True, blank=True)
    completion_note = models.TextField("Abschlussvermerk", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["title"]
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
    STATUS = [("open", "Offen"), ("in_progress", "In Arbeit"), ("done", "Erledigt")]
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name="agenda_items")
    topic = models.ForeignKey(Topic, on_delete=models.PROTECT, related_name="agenda_items")
    working_text = models.TextField("Text für dieses Protokoll", blank=True)
    status = models.CharField("Bearbeitungsstand dieses Tagesordnungspunkts", max_length=12, choices=STATUS, default="open")
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name="assigned_meeting_agenda_items", verbose_name="Abweichend verantwortlich")
    position = models.PositiveIntegerField(default=0)
    carried_forward = models.BooleanField(default=False)
    followup_of = models.OneToOneField("self", on_delete=models.SET_NULL, null=True, blank=True, related_name="followup_item")

    class Meta:
        ordering = ["position", "id"]
        constraints = [models.UniqueConstraint(fields=["meeting", "topic"], name="unique_topic_per_meeting")]

class TopicSnapshot(models.Model):
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name="snapshots")
    topic_title = models.CharField(max_length=240)
    text = models.TextField(blank=True)
    status = models.CharField(max_length=12)
    topic_id = models.PositiveBigIntegerField()
    responsible_name = models.CharField("Verantwortlich", max_length=255, blank=True)

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
    series = models.ForeignKey(MeetingSeries, on_delete=models.SET_NULL, null=True, blank=True, related_name="audit_events")
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


class SeriesAccess(models.Model):
    """Role-based assignment of a user to a meeting series."""
    ROLE_PARTICIPANT = "participant"
    ROLE_MODERATOR = "moderator"
    ROLE_READER = "reader"
    ROLE_CHOICES = [
        (ROLE_PARTICIPANT, "Teilnehmer*in"),
        (ROLE_MODERATOR, "Moderator*in"),
        (ROLE_READER, "Leser*in"),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name="meeting_series_access", verbose_name="Benutzer")
    series = models.ForeignKey(MeetingSeries, on_delete=models.CASCADE,
                               related_name="user_access", verbose_name="Besprechungsreihe")
    role = models.CharField("Rolle", max_length=16, choices=ROLE_CHOICES, default=ROLE_PARTICIPANT)

    class Meta:
        ordering = ["series__name", "user__username"]
        constraints = [
            models.UniqueConstraint(fields=["user", "series"], name="unique_user_series_access")
        ]
        verbose_name = "Serienberechtigung"
        verbose_name_plural = "Serienberechtigungen"

    def __str__(self):
        return f"{self.user} – {self.series}"


class UserProfile(models.Model):
    """Additional display information for an existing Django user account."""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="meeting_profile",
        verbose_name="Benutzer",
    )
    short_description = models.CharField("Kurzbeschreibung", max_length=80, blank=True)

    class Meta:
        verbose_name = "Benutzerprofil"
        verbose_name_plural = "Benutzerprofile"

    def __str__(self):
        return f"{self.user} – {self.short_description}" if self.short_description else str(self.user)


class OrganizationSettings(models.Model):
    """Globale Bezeichnung der Organisationseinheit für den Meeting Manager."""

    name = models.CharField(
        "Organisationseinheit", max_length=160, blank=True, default="",
        help_text='Zum Beispiel „Fachbereich 20“. Die Angabe erscheint in der Anwendungs-Kopfzeile und in Protokollen.',
    )
    short_name = models.CharField(
        "Kurzbezeichnung", max_length=24, blank=True, default="MM",
        help_text='Kompakte Anzeige im eingeklappten Seitenmenü, zum Beispiel „FB 20“ oder „FB20“.',
    )
    primary_color = models.CharField("Primärfarbe", max_length=7, default="#00549F", validators=[RegexValidator(r"^#[0-9A-Fa-f]{6}$", "Bitte einen HEX-Farbwert im Format #RRGGBB eingeben.")], help_text="Grundfarbe für Navigation, Links und primäre Schaltflächen.")
    primary_color_light = models.CharField("Primärfarbe – Hellmodus", max_length=7, blank=True, default="", validators=[RegexValidator(r"^$|^#[0-9A-Fa-f]{6}$", "Bitte einen HEX-Farbwert im Format #RRGGBB eingeben oder leer lassen.")], help_text="Optional. Leer = Primärfarbe verwenden.")
    primary_color_dark = models.CharField("Primärfarbe – Dunkelmodus", max_length=7, blank=True, default="", validators=[RegexValidator(r"^$|^#[0-9A-Fa-f]{6}$", "Bitte einen HEX-Farbwert im Format #RRGGBB eingeben oder leer lassen.")], help_text="Optional. Leer = Primärfarbe verwenden.")
    secondary_color = models.CharField("Sekundärfarbe", max_length=7, default="#8FC5FF", validators=[RegexValidator(r"^#[0-9A-Fa-f]{6}$", "Bitte einen HEX-Farbwert im Format #RRGGBB eingeben.")], help_text="Ergänzende Akzente, dezente Hervorhebungen und unterstützende Flächen.")
    secondary_color_light = models.CharField("Sekundärfarbe – Hellmodus", max_length=7, blank=True, default="", validators=[RegexValidator(r"^$|^#[0-9A-Fa-f]{6}$", "Bitte einen HEX-Farbwert im Format #RRGGBB eingeben oder leer lassen.")], help_text="Optional. Leer = Sekundärfarbe verwenden.")
    secondary_color_dark = models.CharField("Sekundärfarbe – Dunkelmodus", max_length=7, blank=True, default="", validators=[RegexValidator(r"^$|^#[0-9A-Fa-f]{6}$", "Bitte einen HEX-Farbwert im Format #RRGGBB eingeben oder leer lassen.")], help_text="Optional. Leer = Sekundärfarbe verwenden.")
    tertiary_color = models.CharField("Tertiärfarbe", max_length=7, default="#FFCC00", validators=[RegexValidator(r"^#[0-9A-Fa-f]{6}$", "Bitte einen HEX-Farbwert im Format #RRGGBB eingeben.")], help_text="Markierungen und besondere visuelle Hervorhebungen.")
    tertiary_color_light = models.CharField("Tertiärfarbe – Hellmodus", max_length=7, blank=True, default="", validators=[RegexValidator(r"^$|^#[0-9A-Fa-f]{6}$", "Bitte einen HEX-Farbwert im Format #RRGGBB eingeben oder leer lassen.")], help_text="Optional. Leer = Tertiärfarbe verwenden.")
    tertiary_color_dark = models.CharField("Tertiärfarbe – Dunkelmodus", max_length=7, blank=True, default="", validators=[RegexValidator(r"^$|^#[0-9A-Fa-f]{6}$", "Bitte einen HEX-Farbwert im Format #RRGGBB eingeben oder leer lassen.")], help_text="Optional. Leer = Tertiärfarbe verwenden.")

    class Meta:
        verbose_name = "Organisationseinstellung"
        verbose_name_plural = "Organisationseinstellungen"

    def save(self, *args, **kwargs):
        # Es gibt genau einen globalen Konfigurationsdatensatz.
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Den Datensatz nicht entfernen, sondern die Bezeichnung leeren.
        self.name = ""
        self.save(update_fields=["name"])

    @classmethod
    def current_brand_colors(cls):
        defaults = {"primary_color": "#00549F", "secondary_color": "#8FC5FF", "tertiary_color": "#FFCC00"}
        settings = cls.objects.filter(pk=1).first()
        colors = {}
        for name, default in defaults.items():
            base = getattr(settings, name, "") or default
            colors[name] = base
            colors[f"{name}_light"] = (getattr(settings, f"{name}_light", "") or base) if settings else base
            colors[f"{name}_dark"] = (getattr(settings, f"{name}_dark", "") or base) if settings else base
        return colors

    @classmethod
    def current_short_name(cls):
        settings = cls.objects.filter(pk=1).only("short_name").first()
        return settings.short_name.strip() if settings and settings.short_name else "MM"

    @classmethod
    def current_name(cls):
        settings = cls.objects.filter(pk=1).only("name").first()
        return settings.name.strip() if settings and settings.name else ""

    def __str__(self):
        return self.name or "Organisationseinheit (nicht festgelegt)"
