from django import forms
from django.contrib.auth import get_user_model
from .models import Topic, AgendaItem, TopicAttachment, MeetingSeries
class UsernameLoginForm(forms.Form):
    username = forms.CharField(label="Benutzername", max_length=150)
class TopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ["title","description","due_date","status","series"]
        widgets = {"due_date": forms.DateInput(attrs={"type":"date"}), "description": forms.Textarea(attrs={"rows":5})}
class AgendaTextForm(forms.ModelForm):
    class Meta:
        model = AgendaItem
        fields = ["working_text"]
        widgets = {"working_text": forms.Textarea(attrs={"rows":7})}
class AttachmentForm(forms.ModelForm):
    class Meta:
        model = TopicAttachment
        fields = ["label","uploaded_file","network_path"]
class SeriesForm(forms.ModelForm):
    class Meta:
        model = MeetingSeries
        fields = ["name","description","active","recurrence","weekday","start_date","end_date"]
        widgets = {"start_date": forms.DateInput(attrs={"type":"date"}), "end_date": forms.DateInput(attrs={"type":"date"})}
