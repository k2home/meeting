from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model
from django.db.models import Exists, OuterRef
from .models import Topic, AgendaItem, TopicAttachment, MeetingSeries, TopicComment, Meeting, SeriesAccess
from .user_display import user_display_name

class UsernameLoginForm(AuthenticationForm):
    username = forms.CharField(label="Benutzername", max_length=150)
    password = forms.CharField(label="Passwort", strip=False, widget=forms.PasswordInput)

class UserDisplayModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return user_display_name(obj)


class TopicForm(forms.ModelForm):
    assigned_to = UserDisplayModelChoiceField(queryset=get_user_model().objects.none(), required=False, label="Verantwortlich")

    class Meta:
        model = Topic
        fields = ["title", "description", "due_date", "status", "series", "assigned_to"]
        widgets = {
            "due_date": forms.DateInput(attrs={"type": "date"}),
            "description": forms.Textarea(attrs={"rows": 5}),
        }

    def __init__(self, *args, series_queryset=None, series_required=False, **kwargs):
        super().__init__(*args, **kwargs)
        if series_queryset is not None:
            self.fields["series"].queryset = series_queryset
            self.fields["series"].required = series_required
        User = get_user_model()
        self.fields["assigned_to"].queryset = User.objects.filter(is_active=True).order_by("username")
        self.fields["assigned_to"].required = False
        self.fields["assigned_to"].empty_label = "Nicht zugewiesen"


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

class AttachmentForm(forms.ModelForm):
    class Meta:
        model = TopicAttachment
        fields = ["label", "uploaded_file", "network_path"]

class SeriesForm(forms.ModelForm):
    weekday = forms.TypedChoiceField(
        label="Wochentag", choices=[(0, "Montag"), (1, "Dienstag"), (2, "Mittwoch"),
                                  (3, "Donnerstag"), (4, "Freitag"), (5, "Samstag"), (6, "Sonntag")],
        coerce=int,
    )

    class Meta:
        model = MeetingSeries
        fields = ["name", "description", "active", "recurrence", "weekday", "start_date", "end_date"]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
        }


class CompactParticipantSelect(forms.CheckboxSelectMultiple):
    template_name = "meetings/widgets/participant_select.html"

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["widget"]["reader_users"] = getattr(self, "reader_users", [])
        return context


class ParticipantMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        label = user_display_name(obj)
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
        reader_membership = User.objects.filter(
            pk=OuterRef("pk"), groups__name="Leser*in"
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
    class Meta:
        model = Meeting
        fields = ["date"]
        widgets = {"date": forms.DateInput(attrs={"type": "date"})}
