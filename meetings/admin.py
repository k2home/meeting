from django import forms
from django.contrib import admin, messages
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import (
    GroupAdmin as DjangoGroupAdmin,
    UserAdmin as DjangoUserAdmin,
    UserChangeForm as DjangoUserChangeForm,
)
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.template.response import TemplateResponse
from django.urls import path

from .models import (
    MeetingSeries, Meeting, Topic, AgendaItem, TopicSnapshot, TopicAttachment,
    TopicTransferHistory, AuditEvent, TopicComment, SeriesAccess, UserProfile, OrganizationSettings,
)
from .user_display import user_display_name, user_display_name_with_login
from .user_csv import export_users_csv, import_users_csv
from .topic_csv import export_topic_agenda_csv, import_topic_agenda_csv, sample_csv_response

User = get_user_model()

admin.site.site_header = "Meeting Manager – Verwaltung"
admin.site.site_title = "Meeting Manager"
admin.site.index_title = "Daten und Benutzer verwalten"


class MeetingInline(admin.TabularInline):
    model = Meeting
    extra = 0


class SeriesAccessInline(admin.TabularInline):
    model = SeriesAccess
    extra = 1

    def get_fields(self, request, obj=None):
        return ("user", "role") if self.parent_model == MeetingSeries else ("series", "role")


@admin.register(MeetingSeries)
class SeriesAdmin(admin.ModelAdmin):
    list_display = ("name", "recurrence", "active", "start_date", "end_date")
    inlines = [MeetingInline, SeriesAccessInline]


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ("series", "date", "finalized_at")
    list_filter = ("series", "finalized_at")
    filter_horizontal = ("participants",)

    def get_readonly_fields(self, request, obj=None):
        return ("participants",) if obj and obj.finalized_at else ()


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    change_list_template = "admin/meetings/topic_changelist.html"

    def get_urls(self):
        custom_urls = [
            path("csv-import/", self.admin_site.admin_view(self.csv_import_view), name="meetings_topic_csv_import"),
            path("csv-sample/", self.admin_site.admin_view(self.csv_sample_view), name="meetings_topic_csv_sample"),
            path("csv-export/", self.admin_site.admin_view(self.csv_export_view), name="meetings_topic_csv_export"),
        ]
        return custom_urls + super().get_urls()

    def csv_import_view(self, request):
        if not self.has_change_permission(request):
            raise PermissionDenied
        return import_topic_agenda_csv(request)

    def csv_sample_view(self, request):
        if not self.has_view_or_change_permission(request):
            raise PermissionDenied
        return sample_csv_response()

    def csv_export_view(self, request):
        if not self.has_view_or_change_permission(request):
            raise PermissionDenied
        return export_topic_agenda_csv(request)

    list_display = ("title", "series", "assigned_to", "status")
    list_filter = ("series", "status")
    search_fields = ("title", "description")


@admin.register(TopicTransferHistory)
class TopicTransferHistoryAdmin(admin.ModelAdmin):
    list_display = ("topic", "from_series", "to_series", "transferred_at", "transferred_by")
    list_filter = ("from_series", "to_series", "transferred_at")
    search_fields = ("topic__title", "note")
    readonly_fields = ("topic", "from_series", "to_series", "transferred_at", "transferred_by", "note")


admin.site.register(AgendaItem)
admin.site.register(TopicSnapshot)
admin.site.register(TopicAttachment)


@admin.register(AuditEvent)
class AuditEventAdmin(admin.ModelAdmin):
    list_display = ("created_at", "action", "summary", "actor", "topic", "meeting")
    list_filter = ("action", "created_at")
    search_fields = ("summary", "topic__title", "actor__username")
    readonly_fields = ("created_at", "action", "summary", "actor", "topic", "meeting", "changes")

    def has_view_permission(self, request, obj=None):
        return request.user.is_active and request.user.is_staff

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(TopicComment)
class TopicCommentAdmin(admin.ModelAdmin):
    list_display = ("topic", "author", "created_at")
    search_fields = ("topic__title", "body", "author__username")
    readonly_fields = ("topic", "author", "body", "created_at")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(SeriesAccess)
class SeriesAccessAdmin(admin.ModelAdmin):
    list_display = ("display_user", "series", "role")
    list_filter = ("series", "role")
    search_fields = ("user__username", "user__first_name", "user__last_name", "series__name")

    @admin.display(description="Benutzer", ordering="user__username")
    def display_user(self, obj):
        return user_display_name_with_login(obj.user)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        field = super().formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name == "user":
            field.label_from_instance = user_display_name_with_login
        return field


class MeetingGroupAdmin(DjangoGroupAdmin):
    """Die Admin-Seite „Gruppen“ verwaltet die Mitgliedschaften je Besprechungsreihe."""

    change_list_template = "admin/auth/group/change_list.html"

    def changelist_view(self, request, extra_context=None):
        if not self.has_view_or_change_permission(request):
            raise PermissionDenied

        if request.method == "POST":
            if not self.has_change_permission(request):
                raise PermissionDenied
            action = request.POST.get("action")
            try:
                with transaction.atomic():
                    if action == "add":
                        series = MeetingSeries.objects.get(pk=request.POST.get("series_id"))
                        user = User.objects.get(pk=request.POST.get("user_id"))
                        role = request.POST.get("role")
                        if role not in dict(SeriesAccess.ROLE_CHOICES):
                            raise ValueError("Bitte eine gültige Serienberechtigung auswählen.")
                        access, created = SeriesAccess.objects.get_or_create(
                            series=series, user=user, defaults={"role": role}
                        )
                        if not created:
                            access.role = role
                            access.save(update_fields=["role"])
                        messages.success(request, f"{user_display_name(user)} wurde der Gruppe „{series.name}“ zugeordnet.")
                    elif action == "update":
                        access = SeriesAccess.objects.select_related("series", "user").get(
                            pk=request.POST.get("access_id")
                        )
                        role = request.POST.get("role")
                        if role not in dict(SeriesAccess.ROLE_CHOICES):
                            raise ValueError("Bitte eine gültige Serienberechtigung auswählen.")
                        access.role = role
                        access.save(update_fields=["role"])
                        messages.success(request, f"Berechtigung für {user_display_name(access.user)} in „{access.series.name}“ aktualisiert.")
                    elif action == "remove":
                        access = SeriesAccess.objects.select_related("series", "user").get(
                            pk=request.POST.get("access_id")
                        )
                        label = f"{user_display_name(access.user)} aus „{access.series.name}“"
                        access.delete()
                        messages.success(request, f"{label} entfernt.")
                    else:
                        raise ValueError("Unbekannte Aktion.")
            except (MeetingSeries.DoesNotExist, User.DoesNotExist, SeriesAccess.DoesNotExist):
                messages.error(request, "Die ausgewählte Serie, Person oder Zuordnung wurde nicht gefunden.")
            except ValueError as exc:
                messages.error(request, str(exc))
            from django.shortcuts import redirect
            return redirect("admin:auth_group_changelist")

        series_rows = []
        for series in MeetingSeries.objects.prefetch_related("user_access__user").all():
            series_rows.append({
                "series": series,
                "members": list(series.user_access.select_related("user").all()),
            })

        context = {
            **self.admin_site.each_context(request),
            "title": "Gruppen – Serien und Berechtigungen",
            "opts": self.model._meta,
            "series_rows": series_rows,
            "available_users": User.objects.all().order_by("username"),
            "role_choices": SeriesAccess.ROLE_CHOICES,
            "has_add_permission": self.has_change_permission(request),
            "has_change_permission": self.has_change_permission(request),
        }
        context.update(extra_context or {})
        return TemplateResponse(request, self.change_list_template, context)


class MeetingUserChangeForm(DjangoUserChangeForm):
    short_description = forms.CharField(
        label="Kurzbeschreibung", required=False, max_length=80,
    )
    is_administrator = forms.BooleanField(
        label="Administrator", required=False,
        help_text="Gewährt globale Administratorrechte für alle Besprechungsreihen.",
    )

    class Meta(DjangoUserChangeForm.Meta):
        model = User
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            profile = getattr(self.instance, "meeting_profile", None)
            self.fields["short_description"].initial = (
                profile.short_description if profile else ""
            )
        self.fields["is_superuser"].label = "Django-Superuser"
        self.fields["is_administrator"].initial = (
            self.instance.groups.filter(name="Admin").exists()
            if self.instance and self.instance.pk else False
        )
        self.fields.pop("groups", None)
        self.fields.pop("user_permissions", None)


class MeetingUserAdmin(DjangoUserAdmin):
    change_list_template = "admin/auth/user/change_list.html"

    def get_urls(self):
        custom_urls = [
            path("csv-export/", self.admin_site.admin_view(self.csv_export_view), name="auth_user_csv_export"),
            path("csv-import/", self.admin_site.admin_view(self.csv_import_view), name="auth_user_csv_import"),
        ]
        return custom_urls + super().get_urls()

    def _check_csv_permission(self, request):
        if not self.has_change_permission(request):
            raise PermissionDenied

    def csv_export_view(self, request):
        self._check_csv_permission(request)
        return export_users_csv(request)

    def csv_import_view(self, request):
        self._check_csv_permission(request)
        return import_users_csv(request)

    form = MeetingUserChangeForm
    inlines = [SeriesAccessInline]
    change_form_template = "admin/auth/user/change_form.html"
    list_display = ("display_name_with_login", "is_staff", "is_active")
    fieldsets = (
        ("Persönliche Informationen", {
            "fields": ("username", "first_name", "last_name", "email", "short_description"),
        }),
        ("Berechtigungen", {
            "fields": ("is_active", "is_administrator", "is_superuser"),
        }),
        ("Wichtige Daten", {
            "fields": ("last_login", "date_joined"),
        }),
    )
    readonly_fields = ("last_login", "date_joined")
    filter_horizontal = ("groups",)

    @admin.display(description="Person (Anmeldename)")
    def display_name_with_login(self, obj):
        return user_display_name_with_login(obj)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        user = form.instance
        UserProfile.objects.update_or_create(
            user=user,
            defaults={"short_description": form.cleaned_data.get("short_description", "")},
        )
        admin_group, _ = Group.objects.get_or_create(name="Admin")
        if form.cleaned_data.get("is_administrator", False):
            user.groups.add(admin_group)
        else:
            user.groups.remove(admin_group)
        should_be_staff = user.is_superuser or user.groups.filter(name="Admin").exists()
        if user.is_staff != should_be_staff:
            user.is_staff = should_be_staff
            user.save(update_fields=["is_staff"])


admin.site.unregister(User)
admin.site.unregister(Group)
admin.site.register(User, MeetingUserAdmin)
admin.site.register(Group, MeetingGroupAdmin)


@admin.register(OrganizationSettings)
class OrganizationSettingsAdmin(admin.ModelAdmin):
    list_display = ("name",)
    fields = ("name", "short_name", "accent_color", "accent_color_light", "accent_color_dark")

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        if db_field.name.startswith("accent_color") and formfield:
            formfield.widget.attrs.update({
                "placeholder": "#00549F",
                "pattern": r"^#[0-9A-Fa-f]{6}$" if db_field.name == "accent_color" else r"^$|^#[0-9A-Fa-f]{6}$",
                "spellcheck": "false",
            })
        return formfield

    def has_add_permission(self, request):
        return super().has_add_permission(request) and not OrganizationSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
