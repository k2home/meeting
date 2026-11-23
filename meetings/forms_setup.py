import hmac
import os

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm


class InitialAdministratorForm(UserCreationForm):
    first_name = forms.CharField(label="Vorname", max_length=150)
    last_name = forms.CharField(label="Nachname", max_length=150)
    email = forms.EmailField(label="E-Mail-Adresse")
    setup_token = forms.CharField(label="Einrichtungscode", widget=forms.PasswordInput(attrs={"autocomplete": "off"}), strip=False)

    def clean_setup_token(self):
        supplied = self.cleaned_data["setup_token"]
        expected = os.environ.get("SETUP_TOKEN", "")
        if not expected or not hmac.compare_digest(supplied, expected):
            raise forms.ValidationError("Der Einrichtungscode ist ungültig. Bitte verwende den Code aus der Installationsausgabe.")
        return supplied

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ("username", "first_name", "last_name", "email")
