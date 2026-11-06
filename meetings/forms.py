from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Topic, AgendaItem, TopicAttachment, MeetingSeries, Meeting


class UsernameLoginForm(AuthenticationForm):
    username = forms.CharField(label="Benutzername", max_length=150)
    password = forms.CharField(label="Passwort", strip=False, widget=forms.PasswordInput)


class TopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ["title", "description", "due_date", "status", "series"]
        widgets = {
            "due_date": forms.DateInput(attrs={"type": "date"}),
            "description": forms.Textarea(attrs={"rows": 5}),
        }


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


class MeetingForm(forms.ModelForm):
    class Meta:
        model = Meeting
        fields = ["series", "date", "title"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "title": forms.TextInput(attrs={"placeholder": "Optionaler Titel"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["series"].queryset = MeetingSeries.objects.filter(active=True)
        self.fields["series"].label = "Besprechungsreihe"
        self.fields["date"].label = "Termin"
        self.fields["title"].label = "Titel (optional)"


class MeetingDateForm(forms.ModelForm):
    class Meta:
        model = Meeting
        fields = ["date", "title"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "title": forms.TextInput(attrs={"placeholder": "Optionaler Titel"}),
        }
