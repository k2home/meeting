from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model
from .models import Topic, AgendaItem, TopicAttachment, MeetingSeries, TopicComment, Meeting

class UsernameLoginForm(AuthenticationForm):
    username = forms.CharField(label="Benutzername", max_length=150)
    password = forms.CharField(label="Passwort", strip=False, widget=forms.PasswordInput)

class TopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ["title", "description", "due_date", "status", "series", "assigned_to"]
        widgets = {
            "due_date": forms.DateInput(attrs={"type": "date"}),
            "description": forms.Textarea(attrs={"rows": 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
    class Meta:
        model = MeetingSeries
        fields = ["name", "description", "active", "recurrence", "weekday", "start_date", "end_date"]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
        }


class MeetingParticipantsForm(forms.ModelForm):
    class Meta:
        model = Meeting
        fields = ["participants"]
        widgets = {"participants": forms.CheckboxSelectMultiple}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        User = get_user_model()
        self.fields["participants"].queryset = User.objects.filter(is_active=True).order_by("last_name", "first_name", "username")
        self.fields["participants"].required = False
        self.fields["participants"].label = "Teilnehmer auswählen"
