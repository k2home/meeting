from zoneinfo import available_timezones

from django import forms
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import password_validation
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from .access import is_admin
from .models import MeetingSeries, OrganizationSettings, SeriesAccess, UserProfile
from .user_csv import export_users_csv, import_users_csv
from .topic_csv import export_topic_agenda_csv, import_topic_agenda_csv, sample_csv_response
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
        self.fields["last_login"] = forms.CharField(label="Letzte Anmeldung", required=False, disabled=True, initial=self.instance.last_login.strftime("%d.%m.%Y, %H:%M") if self.instance.last_login else "Noch nie")
        self.fields["date_joined"] = forms.CharField(label="Erstellt am", required=False, disabled=True, initial=self.instance.date_joined.strftime("%d.%m.%Y, %H:%M") if self.instance.date_joined else "–")
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
            "name", "short_name", "logo", "timezone", "attachment_max_size_mb",
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
    return render(request, "meetings/management_users.html", {
        "users": [{"account": user, "is_administrator": is_admin(user)} for user in users],
        "role_choices": SeriesAccess.ROLE_CHOICES,
    })


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

    access_qs = SeriesAccess.objects.select_related("series", "user").all()
    query = request.GET.get("q", "").strip()
    role_filter = request.GET.get("role", "")
    if query:
        from django.db.models import Q
        access_qs = access_qs.filter(Q(user__username__icontains=query) | Q(user__first_name__icontains=query) | Q(user__last_name__icontains=query) | Q(series__name__icontains=query))
    if role_filter in dict(SeriesAccess.ROLE_CHOICES):
        access_qs = access_qs.filter(role=role_filter)
    access_ids = set(access_qs.values_list("pk", flat=True))
    series_rows = [{
        "series": series,
        "members": [a for a in series.user_access.select_related("user").all() if a.pk in access_ids],
    } for series in MeetingSeries.objects.order_by("name")]
    series_rows = [row for row in series_rows if row["members"] or not (query or role_filter)]
    return render(request, "meetings/management_groups.html", {
        "series_rows": series_rows,
        "available_users": User.objects.order_by("last_name", "first_name", "username"),
        "search": request.GET.get("q", ""),
        "role_filter": request.GET.get("role", ""),
        "role_choices": SeriesAccess.ROLE_CHOICES,
    })


@login_required
def management_settings(request):
    _require_admin(request)
    instance = OrganizationSettings.objects.filter(pk=1).first() or OrganizationSettings()
    form = OrganizationSettingsForm(request.POST or None, instance=instance)
    if request.method == "POST" and form.is_valid():
        settings_obj = form.save(commit=False)
        settings_obj.full_clean()
        settings_obj.save()
        messages.success(request, "Die Organisationseinstellungen wurden gespeichert.")
        return redirect("management_settings")
    return render(request, "meetings/management_settings.html", {"form": form})


@login_required
def management_data(request):
    _require_admin(request)
    return render(request, "meetings/management_data.html")


@login_required
def management_user_password_reset(request, pk):
    _require_admin(request)
    user = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        from django.contrib.auth.tokens import default_token_generator
        from django.utils.http import urlsafe_base64_encode
        from django.utils.encoding import force_bytes
        from django.urls import reverse
        from django.contrib.sites.shortcuts import get_current_site
        from django.core.mail import send_mail
        from django.template.loader import render_to_string
        from django.utils.html import strip_tags
        from django.contrib.auth.forms import PasswordResetForm
        form = PasswordResetForm({"email": user.email})
        if not user.email or not form.is_valid():
            messages.error(request, "Für diesen Nutzer ist keine gültige E-Mail-Adresse hinterlegt.")
        else:
            form.save(
                request=request,
                use_https=request.is_secure(),
                email_template_name="registration/password_reset_email.html",
                subject_template_name="registration/password_reset_subject.txt",
                domain_override=get_current_site(request).domain,
            )
            messages.success(request, "Die Passwort-Zurücksetzen-Mail wurde angefordert.")
        return redirect("management_user_edit", pk=user.pk)
    return render(request, "meetings/management_password_reset.html", {"account": user})


@login_required
def management_user_series(request, pk):
    _require_admin(request)
    user = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        selected = request.POST.getlist("series")
        roles = request.POST
        with transaction.atomic():
            for series in MeetingSeries.objects.all():
                role = roles.get(f"role_{series.pk}")
                if str(series.pk) in selected and role in dict(SeriesAccess.ROLE_CHOICES):
                    SeriesAccess.objects.update_or_create(user=user, series=series, defaults={"role": role})
                else:
                    SeriesAccess.objects.filter(user=user, series=series).delete()
        messages.success(request, "Besprechungsreihen-Zuordnungen wurden gespeichert.")
        return redirect("management_user_edit", pk=user.pk)
    return render(request, "meetings/management_user_series.html", {
        "account": user, "series_rows": [{
            "series": series,
            "access": SeriesAccess.objects.filter(user=user, series=series).first(),
        } for series in MeetingSeries.objects.order_by("name")],
        "role_choices": SeriesAccess.ROLE_CHOICES,
    })


@login_required
def management_user_csv_export(request):
    _require_admin(request)
    return export_users_csv(request)


@login_required
def management_user_csv_import(request):
    _require_admin(request)
    return import_users_csv(request)


@login_required
def management_topic_csv_export(request):
    _require_admin(request)
    return export_topic_agenda_csv(request)


@login_required
def management_topic_csv_sample(request):
    _require_admin(request)
    return sample_csv_response()


@login_required
def management_topic_csv_import(request):
    _require_admin(request)
    return import_topic_agenda_csv(request)


@login_required
def management_user_csv_sample(request):
    _require_admin(request)
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="benutzer-muster.csv"'
    response.write("\ufeff")
    response.write(
        "# Musterdatei fuer den Nutzerimport. UTF-8-Kodierung, Semikolon als Trennzeichen.\r\n"
        "# Kommentarzeilen mit # werden beim Import ignoriert und koennen in der Datei stehen bleiben.\r\n"
        "# username: Pflichtfeld; eindeutiger Anmeldename, maximal 150 Zeichen.\r\n"
        "# first_name: Vorname; optionaler Freitext.\r\n"
        "# last_name: Nachname; optionaler Freitext.\r\n"
        "# email: E-Mail-Adresse; optional, muss bei Angabe eindeutig sein.\r\n"
        "# short_description: Kurzbeschreibung; optional, maximal 80 Zeichen.\r\n"
        "# is_active: Konto aktivieren; erlaubt: true/false, 1/0, ja/nein, yes/no, aktiv/inaktiv, aktiviert/deaktiviert.\r\n"
        "# series: Name einer bereits vorhandenen Besprechungsreihe; optional, Schreibweise muss exakt uebereinstimmen.\r\n"
        "# series_role: Rolle fuer die angegebene Reihe; erlaubt: participant, teilnehmer*in, moderator, moderator*in, reader, leser*in.\r\n"
        "# series_role bleibt leer, wenn keine series angegeben ist. Bei mehreren Reihen je Benutzer eine Zeile verwenden; Nutzerdaten identisch halten.\r\n"
        "# is_administrator: Optionale globale Administratorrolle; erlaubt dieselben Ja/Nein-Werte wie is_active. Nur globale Administratoren duerfen dieses Feld importieren.\r\n"
        "# Neue Benutzer erhalten ein zufaelliges Startpasswort; anschliessend ist die Passwort-zuruecksetzen-Funktion zu verwenden.\r\n"
        "username;first_name;last_name;email;short_description;is_active;series;series_role;is_administrator\r\n"
        "musterbenutzer;Max;Mustermann;max.mustermann@example.org;Beispielkonto;true;;;false\r\n"
    )
    return response
