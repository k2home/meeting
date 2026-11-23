from zoneinfo import available_timezones

from django import forms
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from .access import is_admin
from .models import MeetingSeries, OrganizationSettings, SeriesAccess, UserProfile
from .user_display import user_display_name_with_login
from .user_roles import sync_admin_access

User = get_user_model()


def _require_admin(request):
    if not is_admin(request.user):
        raise PermissionDenied


class ManagedUserCreateForm(UserCreationForm):
    first_name = forms.CharField(label="Vorname", max_length=150, required=False)
    last_name = forms.CharField(label="Nachname", max_length=150, required=False)
    email = forms.EmailField(label="E-Mail-Adresse", required=False)
    short_description = forms.CharField(label="Kurzbeschreibung", max_length=80, required=False)
    is_administrator = forms.BooleanField(label="Administrator", required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "last_name", "email")

    def save(self, commit=True):
        user = super().save(commit=False)
        for field in ("first_name", "last_name", "email"):
            setattr(user, field, self.cleaned_data.get(field, "").strip())
        if commit:
            user.save()
            UserProfile.objects.update_or_create(
                user=user, defaults={"short_description": self.cleaned_data.get("short_description", "").strip()}
            )
            sync_admin_access(user, self.cleaned_data.get("is_administrator", False))
        return user


class ManagedUserEditForm(forms.ModelForm):
    short_description = forms.CharField(label="Kurzbeschreibung", max_length=80, required=False)
    is_administrator = forms.BooleanField(label="Administrator", required=False)

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "is_active")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].disabled = True
        profile = getattr(self.instance, "meeting_profile", None) if self.instance.pk else None
        self.fields["short_description"].initial = profile.short_description if profile else ""
        self.fields["is_administrator"].initial = (
            self.instance.groups.filter(name="Admin").exists() if self.instance.pk else False
        )

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            UserProfile.objects.update_or_create(
                user=user, defaults={"short_description": self.cleaned_data.get("short_description", "").strip()}
            )
            sync_admin_access(user, self.cleaned_data.get("is_administrator", False))
        return user


class OrganizationSettingsForm(forms.ModelForm):
    timezone = forms.ChoiceField(
        label="Zeitzone",
        choices=[(zone, zone) for zone in sorted(available_timezones())],
    )

    class Meta:
        model = OrganizationSettings
        fields = (
            "name", "short_name", "timezone", "attachment_max_size_mb",
            "primary_color", "primary_color_light", "primary_color_dark",
            "secondary_color", "secondary_color_light", "secondary_color_dark",
            "tertiary_color", "tertiary_color_light", "tertiary_color_dark",
        )


@login_required
def management_home(request):
    _require_admin(request)
    return render(request, "meetings/management.html", {
        "user_count": User.objects.count(),
        "active_user_count": User.objects.filter(is_active=True).count(),
        "series_count": MeetingSeries.objects.count(),
    })


@login_required
def management_users(request):
    _require_admin(request)
    users = User.objects.all().order_by("last_name", "first_name", "username")
    return render(request, "meetings/management_users.html", {"users": users})


@login_required
def management_user_edit(request, pk=None):
    _require_admin(request)
    instance = get_object_or_404(User, pk=pk) if pk else None
    if instance:
        form = ManagedUserEditForm(request.POST or None, instance=instance)
    else:
        form = ManagedUserCreateForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        if instance and instance.pk == request.user.pk and not form.cleaned_data["is_active"]:
            form.add_error("is_active", "Das eigene Administratorkonto kann hier nicht deaktiviert werden.")
        else:
            with transaction.atomic():
                user = form.save()
            messages.success(request, f"Benutzer „{user_display_name_with_login(user)}“ wurde gespeichert.")
            return redirect("management_users")
    return render(request, "meetings/management_user_form.html", {
        "form": form, "page_title": "Benutzer bearbeiten" if instance else "Benutzer hinzufügen",
        "is_new": instance is None,
    })


@login_required
def management_groups(request):
    _require_admin(request)
    if request.method == "POST":
        action = request.POST.get("action")
        try:
            with transaction.atomic():
                if action == "add":
                    series = get_object_or_404(MeetingSeries, pk=request.POST.get("series_id"))
                    user = get_object_or_404(User, pk=request.POST.get("user_id"))
                    role = request.POST.get("role")
                    if role not in dict(SeriesAccess.ROLE_CHOICES):
                        raise ValueError("Bitte eine gültige Berechtigung auswählen.")
                    access, created = SeriesAccess.objects.get_or_create(
                        series=series, user=user, defaults={"role": role}
                    )
                    if not created:
                        access.role = role
                        access.save(update_fields=["role"])
                    messages.success(request, f"{user_display_name_with_login(user)} wurde der Gruppe „{series.name}“ zugeordnet.")
                elif action == "update":
                    access = get_object_or_404(SeriesAccess.objects.select_related("series", "user"), pk=request.POST.get("access_id"))
                    role = request.POST.get("role")
                    if role not in dict(SeriesAccess.ROLE_CHOICES):
                        raise ValueError("Bitte eine gültige Berechtigung auswählen.")
                    access.role = role
                    access.save(update_fields=["role"])
                    messages.success(request, "Die Gruppenberechtigung wurde aktualisiert.")
                elif action == "remove":
                    access = get_object_or_404(SeriesAccess.objects.select_related("series", "user"), pk=request.POST.get("access_id"))
                    label = f"{user_display_name_with_login(access.user)} aus „{access.series.name}“"
                    access.delete()
                    messages.success(request, f"{label} wurde entfernt.")
                else:
                    raise ValueError("Unbekannte Aktion.")
        except ValueError as exc:
            messages.error(request, str(exc))
        return redirect("management_groups")

    series_rows = [{
        "series": series,
        "members": series.user_access.select_related("user").all(),
    } for series in MeetingSeries.objects.order_by("name")]
    return render(request, "meetings/management_groups.html", {
        "series_rows": series_rows,
        "available_users": User.objects.filter(is_active=True).order_by("last_name", "first_name", "username"),
        "role_choices": SeriesAccess.ROLE_CHOICES,
    })


@login_required
def management_settings(request):
    _require_admin(request)
    instance = OrganizationSettings.objects.filter(pk=1).first() or OrganizationSettings()
    form = OrganizationSettingsForm(request.POST or None, instance=instance)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Die Organisationseinstellungen wurden gespeichert.")
        return redirect("management_settings")
    return render(request, "meetings/management_settings.html", {"form": form})
