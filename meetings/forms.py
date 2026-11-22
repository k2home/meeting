from datetime import date, timedelta

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model
from django.db.models import Exists, OuterRef
from .models import AgendaItem, TopicAttachment, MeetingSeries, TopicComment, Meeting, SeriesAccess
from .user_display import user_display_name
from django.utils import timezone

class UsernameLoginForm(AuthenticationForm):
    username = forms.CharField(label="Benutzername", max_length=150)
    password = forms.CharField(label="Passwort", strip=False, widget=forms.PasswordInput)

class UserDisplayModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return user_display_name(obj)


class TopicCommentForm(forms.ModelForm):
    class Meta:
        model = TopicComment
        fields = ["body"]
        widgets = {"body": forms.Textarea(attrs={"rows": 3, "placeholder": "Kommentar oder nächste Schritte …"})}


class AgendaTextForm(forms.ModelForm):
    class Meta:
        model = AgendaItem
        fields = ["working_text"]
        widgets = {"working_text": forms.Textarea(attrs={"rows": 7})}


class AgendaItemCreateForm(forms.Form):
    title = forms.CharField(label="Neues Thema", max_length=240)
    working_text = forms.CharField(
        label="Text für dieses Protokoll", required=False,
        widget=forms.Textarea(attrs={"rows": 4}),
    )
    assigned_to = UserDisplayModelChoiceField(queryset=get_user_model().objects.none(), required=False, label="Abweichend verantwortlich für diesen Tagesordnungspunkt")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        active_users = get_user_model().objects.filter(is_active=True).order_by("username")
        self.fields["assigned_to"].queryset = active_users


class AgendaScheduleForm(forms.Form):
    target_series = forms.ModelChoiceField(
        label="Besprechungsserie", queryset=MeetingSeries.objects.none(),
    )
    target_meeting = forms.ModelChoiceField(
        label="Termin", queryset=Meeting.objects.none(),
    )

    def __init__(self, *args, series_queryset=None, meeting_queryset=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["target_series"].queryset = series_queryset or MeetingSeries.objects.none()
        self.fields["target_meeting"].queryset = meeting_queryset or Meeting.objects.none()

    def clean(self):
        cleaned = super().clean()
        series = cleaned.get("target_series")
        meeting = cleaned.get("target_meeting")
        if series and meeting and meeting.series_id != series.pk:
            self.add_error("target_meeting", "Der Termin gehört nicht zur ausgewählten Besprechungsserie.")
        return cleaned


class AttachmentForm(forms.ModelForm):
    class Meta:
        model = TopicAttachment
        fields = ["label", "uploaded_file", "network_path"]

    def clean(self):
        cleaned = super().clean()
        uploaded = cleaned.get("uploaded_file")
        if not uploaded and not (cleaned.get("network_path") or "").strip():
            raise forms.ValidationError("Bitte wähle eine Datei aus oder gib einen Netzwerkpfad bzw. Link an.")
        return cleaned

class SeriesForm(forms.ModelForm):
    weekday = forms.TypedChoiceField(
        label="Wochentag", choices=[(0, "Montag"), (1, "Dienstag"), (2, "Mittwoch"),
                                  (3, "Donnerstag"), (4, "Freitag"), (5, "Samstag"), (6, "Sonntag")],
        coerce=int,
    )
    recurrence_interval = forms.IntegerField(
        label="Intervall (Wochen oder Monate)", min_value=1, max_value=52, initial=1,
        widget=forms.NumberInput(attrs={"min": "1", "max": "52"}),
    )

    class Meta:
        model = MeetingSeries
        fields = ["name", "description", "recurrence", "recurrence_interval", "weekday", "start_date", "end_date"]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
        }

    def clean(self):
        cleaned = super().clean()
        start_date = cleaned.get("start_date")
        end_date = cleaned.get("end_date")
        if start_date and end_date and end_date < start_date:
            self.add_error("end_date", "Das Enddatum darf nicht vor dem Startdatum liegen.")
        return cleaned

    def __init__(self, *args, **kwargs):
        provided_initial = kwargs.get("initial") or {}
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            if self.instance.recurrence == "biweekly":
                self.initial.setdefault("recurrence", "weekly")
                self.initial.setdefault("recurrence_interval", 2)
        else:
            today = timezone.localdate()
            weekday = int(self.initial.get("weekday", self.fields["weekday"].initial or 0))
            self.initial.setdefault("weekday", weekday)
            self.initial.setdefault("recurrence_interval", 1)
            if "start_date" not in provided_initial:
                self.initial["start_date"] = today + timedelta(days=(weekday - today.weekday()) % 7)
            if "end_date" not in provided_initial:
                self.initial["end_date"] = date(today.year + 1, 12, 31)


class CompactParticipantSelect(forms.CheckboxSelectMultiple):
    template_name = "meetings/widgets/participant_select.html"

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["widget"]["reader_users"] = getattr(self, "reader_users", [])
        return context


class ParticipantMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        label = user_display_name(obj, include_short_description=True)
        if getattr(obj, "is_reader", False):
            label += " (Leser*in)"
        elif getattr(obj, "is_series_member", False):
            label += " (Besprechungsserie)"
        return label


class MeetingParticipantsForm(forms.ModelForm):
    participants = ParticipantMultipleChoiceField(
        queryset=get_user_model().objects.none(),
        required=False,
        widget=CompactParticipantSelect,
        label="Teilnehmer",
    )

    class Meta:
        model = Meeting
        fields = ["participants"]
        widgets = {"participants": CompactParticipantSelect}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        User = get_user_model()
        series_id = getattr(self.instance, "series_id", None)
        membership = SeriesAccess.objects.filter(
            series_id=series_id, user_id=OuterRef("pk")
        )
        reader_membership = SeriesAccess.objects.filter(
            series_id=series_id, user_id=OuterRef("pk"), role=SeriesAccess.ROLE_READER
        )
        self.fields["participants"].queryset = (
            User.objects.filter(is_active=True)
            .annotate(
                is_series_member=Exists(membership),
                is_reader=Exists(reader_membership),
            )
            .order_by("-is_series_member", "-is_reader", "last_name", "first_name", "username")
        )


class MeetingDateForm(forms.ModelForm):
    date = forms.DateField(
        input_formats=["%Y-%m-%d"],
        widget=forms.DateInput(
            format="%Y-%m-%d",
            attrs={"type": "date"},
        ),
        label="Neues Datum",
    )

    class Meta:
        model = Meeting
        fields = ["date"]
