from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator, MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models
from django.utils import formats, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


def validate_topic_attachment_size(uploaded_file):
    if not uploaded_file:
        return
    limit = OrganizationSettings.current_attachment_max_size_bytes()
    if uploaded_file.size > limit:
        limit_mb = limit // (1024 * 1024)
        raise ValidationError(f"Die Datei darf höchstens {limit_mb} MB groß sein.")

class MeetingSeries(models.Model):
    name = models.CharField("Bezeichnung", max_length=160, unique=True)
    description = models.TextField("Beschreibung", blank=True)
    active = models.BooleanField("Aktiv", default=True)
    recurrence = models.CharField("Wiederholung", max_length=12, choices=[("weekly", "Wöchentlich"), ("monthly", "Monatlich")], default="monthly")
    recurrence_interval = models.PositiveSmallIntegerField("Wiederholungsintervall", default=1, validators=[MinValueValidator(1), MaxValueValidator(52)])
    weekday = models.PositiveSmallIntegerField("Wochentag (0=Mo)", default=0, validators=[MinValueValidator(0), MaxValueValidator(6)])
    start_date = models.DateField("Startdatum", default=timezone.localdate)
    end_date = models.DateField("Enddatum", null=True, blank=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(weekday__gte=0, weekday__lte=6),
                name="meeting_series_weekday_0_6",
            ),
            models.CheckConstraint(
                condition=models.Q(recurrence_interval__gte=1, recurrence_interval__lte=52),
                name="meeting_series_interval_1_52",
            ),
            models.CheckConstraint(
                condition=models.Q(end_date__isnull=True) | models.Q(end_date__gte=models.F("start_date")),
                name="meeting_series_end_after_start",
            ),
        ]
        verbose_name = "Besprechungsreihe"
        verbose_name_plural = "Besprechungsreihen"

    def clean(self):
        super().clean()
        if self.end_date and self.start_date and self.end_date < self.start_date:
            raise ValidationError({"end_date": "Das Enddatum darf nicht vor dem Startdatum liegen."})

    @property
    def weekday_label(self):
        labels = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
        return labels[self.weekday] if 0 <= self.weekday < len(labels) else "Ungültiger Wochentag"

    def __str__(self):
        return self.name

class Meeting(models.Model):
    series = models.ForeignKey(MeetingSeries, on_delete=models.SET_NULL, null=True, blank=True, related_name="meetings")
    archived_series_name = models.CharField("Ursprüngliche Besprechungsreihe", max_length=160, blank=True)
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
        series_name = (
            self.series.name if self.series_id
            else self.archived_series_name or "Gelöschte Besprechungsreihe"
        )
        return self.title or f"{series_name} – {formats.date_format(self.date, 'DATE_FORMAT')}"

class Topic(models.Model):
    STATUS = [("open", "Offen"), ("in_progress", "In Arbeit"), ("done", "Erledigt"), ("archived", "Archiviert")]
    title = models.CharField("Thema", max_length=240)
    status = models.CharField("Status", max_length=12, choices=STATUS, default="open")
    series = models.ForeignKey(MeetingSeries, on_delete=models.SET_NULL, null=True, blank=True, related_name="topics")
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name="assigned_meeting_topics", verbose_name="Verantwortlich")
    completed_at = models.DateField("Abschlussdatum", null=True, blank=True)
    completion_note = models.TextField("Abschlussvermerk", blank=True)
    archive_previous_status = models.CharField("Status vor Archivierung", max_length=12, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["title"]
        verbose_name = "Thema"
        verbose_name_plural = "Themen"

    def __str__(self):
        return self.title

class ArchivedMeetingAccess(models.Model):
    """Read access retained for former members after a series is deleted."""
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name="archived_access")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="archived_meeting_access")
    role = models.CharField("Ehemalige Rolle", max_length=16, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["meeting", "user"], name="unique_archived_meeting_user")
        ]


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
    followup_date = models.DateField("Wiedervorlage am", null=True, blank=True)
    followup_series_name = models.CharField("Besprechungsreihe der Wiedervorlage", max_length=160, blank=True)

    class Meta:
        ordering = ["id"]

    def get_status_display(self):
        """Use the same human-readable labels as live agenda items."""
        return dict(AgendaItem.STATUS).get(self.status, self.status)


class TopicAttachment(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="attachments")
    label = models.CharField("Bezeichnung", max_length=180)
    uploaded_file = models.FileField("Datei-Upload", upload_to="topic-files/%Y/%m/", blank=True, validators=[validate_topic_attachment_size])
    network_path = models.CharField("Netzwerkpfad / Link", max_length=1000, blank=True)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.label
    @property
    def network_url(self):
        """Return a validated SMB URL; unsupported paths remain plain text."""
        from urllib.parse import urlsplit
        value = (self.network_path or "").strip()
        if not value:
            return ""
        if value.startswith("\\\\"):
            value = "smb://" + value.lstrip("\\").replace("\\", "/")
        elif value.startswith("//"):
            value = "smb:" + value.replace("\\", "/")
        try:
            parsed = urlsplit(value)
        except ValueError:
            return ""
        scheme = parsed.scheme.lower()
        if any(ord(char) < 32 for char in value) or parsed.username or parsed.password:
            return ""
        if scheme in {"http", "https", "smb"}:
            if not parsed.hostname:
                return ""
        elif scheme == "mailto":
            if not parsed.path or "@" not in parsed.path or "?" in parsed.path:
                return ""
        else:
            return ""
        return value



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
        ("deleted", "Gelöscht"),
        ("series_extended", "Terminreihe verlängert"),
        ("series_reset", "Termine neu aufgesetzt"),
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
    ROLE_NONE = "none"
    ROLE_CHOICES = [
        (ROLE_PARTICIPANT, "Teilnehmer*in"),
        (ROLE_MODERATOR, "Moderator*in"),
        (ROLE_READER, "Leser*in"),
    ]
    REQUEST_ROLE_CHOICES = ROLE_CHOICES + [(ROLE_NONE, "Keine")]
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

    timezone = models.CharField(
        "Zeitzone", max_length=64, default="Europe/Berlin",
        help_text="Zeitzone für die Anzeige von Datums- und Uhrzeitangaben, z. B. Europe/Berlin.",
    )
    attachment_max_size_mb = models.PositiveSmallIntegerField(
        "Maximale Dateigröße für Anlagen (MB)", default=20,
        validators=[MinValueValidator(1), MaxValueValidator(24)],
        help_text="Gilt für hochgeladene Themenanlagen. Zulässig sind 1 bis 24 MB.",
    )
    logo = models.FileField(
        "Organisationslogo", upload_to="organization/logo/", blank=True, validators=[FileExtensionValidator(["png", "jpg", "jpeg", "svg"])],
        help_text="Optionales Logo für die Kopfzeile von Protokoll-PDFs. Unterstützte Formate: PNG, JPEG und SVG.",
    )
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

    def clean(self):
        super().clean()
        try:
            ZoneInfo(self.timezone)
        except (ZoneInfoNotFoundError, TypeError, ValueError):
            raise ValidationError({"timezone": "Bitte eine gültige Zeitzone auswählen."})

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
    def current_attachment_max_size_bytes(cls):
        settings = cls.objects.filter(pk=1).only('attachment_max_size_mb').first()
        size_mb = settings.attachment_max_size_mb if settings else 20
        return size_mb * 1024 * 1024

    @classmethod
    def current_name(cls):
        settings = cls.objects.filter(pk=1).only("name").first()
        return settings.name.strip() if settings and settings.name else ""

    def __str__(self):
        return self.name or "Organisationseinheit (nicht festgelegt)"


class SeriesAccessRequest(models.Model):
    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Offen"),
        (STATUS_APPROVED, "Genehmigt"),
        (STATUS_REJECTED, "Abgelehnt"),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="series_access_requests")
    series = models.ForeignKey(MeetingSeries, on_delete=models.CASCADE, related_name="access_requests")
    requested_role = models.CharField("Beantragte Berechtigung", max_length=16, choices=SeriesAccess.REQUEST_ROLE_CHOICES)
    status = models.CharField("Status", max_length=12, choices=STATUS_CHOICES, default=STATUS_PENDING)
    decision_note = models.CharField("Begründung", max_length=500, blank=True)
    decided_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="decided_series_access_requests")
    created_at = models.DateTimeField(auto_now_add=True)
    decided_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["created_at", "pk"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "series"],
                condition=models.Q(status="pending"),
                name="unique_pending_series_access_request",
            )
        ]
        verbose_name = "Berechtigungsantrag"
        verbose_name_plural = "Berechtigungsanträge"

    def __str__(self):
        return f"{self.user} – {self.series} ({self.get_status_display()})"

class EnaioSettings(models.Model):
    """Zentrale enaio-Ablagekonfiguration."""
    root_folder_id = models.CharField("enaio-Ordner-ID", max_length=64, blank=True)
    root_folder_type = models.PositiveIntegerField("enaio-Objekttyp", default=0)
    root_folder_path = models.CharField("Ordnerpfad", max_length=1000, blank=True)
    root_folder_name = models.CharField("Ordnername", max_length=255, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "enaio-Einstellung"
        verbose_name_plural = "enaio-Einstellungen"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.root_folder_path or self.root_folder_id or "enaio-Einstellungen"


class EnaioFilingTarget(models.Model):
    """Persönliches enaio-Ablageziel eines Benutzers."""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="enaio_filing_target")
    object_id = models.CharField("enaio-Ordner-ID", max_length=64)
    object_type = models.PositiveIntegerField("enaio-Objekttyp", default=0)
    display_path = models.CharField("Ordnerpfad", max_length=1000)
    display_name = models.CharField("Ordnername", max_length=255, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Persönliches enaio-Ablageziel"
        verbose_name_plural = "Persönliche enaio-Ablageziele"

    def __str__(self):
        return self.display_path


class EnaioTransfer(models.Model):
    STATUS_CHOICES = [("pending", "Ausstehend"), ("completed", "Abgeschlossen"), ("failed", "Fehlgeschlagen")]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="enaio_transfers")
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name="enaio_transfers")
    token_hash = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    consumed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default="pending")
    error_message = models.CharField(max_length=500, blank=True)

    class Meta:
        ordering = ["-created_at"]

