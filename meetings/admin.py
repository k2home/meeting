from django import forms
from zoneinfo import available_timezones
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
from .user_roles import sync_admin_access
from .user_csv import export_users_csv, import_users_csv
from .topic_csv import export_topic_agenda_csv, import_topic_agenda_csv, sample_csv_response

User = get_user_model()

admin.site.site_header = "Meeting Manager – Verwaltung"
admin.site.site_title = "Meeting Manager"
admin.site.index_title = "Daten und Benutzer verwalten"


class MeetingInline(admin.TabularInline):
    model = Meeting
    extra = 0
    can_delete = False
    readonly_fields = tuple(field.name for field in Meeting._meta.fields) + ("participants",)


class SeriesAccessInline(admin.TabularInline):
    model = SeriesAccess
    extra = 1

    def get_fields(self, request, obj=None):
        return ("user", "role") if self.parent_model == MeetingSeries else ("series", "role")


@admin.register(MeetingSeries)
class SeriesAdmin(admin.ModelAdmin):
    list_display = ("name", "recurrence", "active", "start_date", "end_date")
    inlines = [MeetingInline, SeriesAccessInline]

    def has_delete_permission(self, request, obj=None):
        # Series deletion uses the application workflow to preserve archived access.
        return False


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ("series", "date", "finalized_at")
    list_filter = ("series", "finalized_at")
    filter_horizontal = ("participants",)

    def get_readonly_fields(self, request, obj=None):
        if obj and (obj.finalized_at or obj.snapshots.exists()):
            return tuple(field.name for field in self.model._meta.fields) + ("participants",)
        return ()

    def has_delete_permission(self, request, obj=None):
        # Meeting deletion is handled by the application workflow, which carries
        # agenda items and participants forward and records an audit event.
        return False


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

    fields = ("title", "series")
    list_display = ("title", "series")
    list_filter = ("series",)
    search_fields = ("title",)


@admin.register(TopicTransferHistory)
class TopicTransferHistoryAdmin(admin.ModelAdmin):
    list_display = ("topic", "from_series", "to_series", "transferred_at", "transferred_by")
    list_filter = ("from_series", "to_series", "transferred_at")
    search_fields = ("topic__title", "note")
    readonly_fields = ("topic", "from_series", "to_series", "transferred_at", "transferred_by", "note")


class AgendaItemAdmin(admin.ModelAdmin):
    list_display = ("meeting", "topic", "status", "position")
    list_filter = ("meeting__finalized_at", "status")
    search_fields = ("topic__title", "working_text")

    def get_readonly_fields(self, request, obj=None):
        if obj and (obj.meeting.finalized_at or obj.meeting.snapshots.exists()):
            return tuple(field.name for field in self.model._meta.fields)
        return ()

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "meeting":
            kwargs["queryset"] = Meeting.objects.filter(finalized_at__isnull=True, snapshots__isnull=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def has_delete_permission(self, request, obj=None):
        # Use the application workflow to remove or carry forward agenda items.
        return False


class TopicSnapshotCorrectionForm(forms.ModelForm):
    correction_reason = forms.CharField(
        label="Begründung der Protokollkorrektur",
        help_text="Die Begründung und der vorherige Protokollstand werden unveränderlich protokolliert.",
        widget=forms.Textarea(attrs={"rows": 3}),
    )

    class Meta:
        model = TopicSnapshot
        fields = ("topic_title", "text", "status", "topic_id", "responsible_name", "correction_reason")


class TopicSnapshotAdmin(admin.ModelAdmin):
    form = TopicSnapshotCorrectionForm
    list_display = ("meeting", "topic_title", "status")
    list_filter = ("meeting__finalized_at",)
    readonly_fields = ("meeting",)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        allowed = super().has_change_permission(request, obj)
        return allowed and (obj is None or bool(obj.meeting.finalized_at))

    def save_model(self, request, obj, form, change):
        previous = None
        if change:
            previous = TopicSnapshot.objects.get(pk=obj.pk)
        super().save_model(request, obj, form, change)
        if previous is not None:
            before = {
                "topic_title": previous.topic_title, "text": previous.text,
                "status": previous.status, "topic_id": previous.topic_id,
                "responsible_name": previous.responsible_name,
            }
            after = {
                "topic_title": obj.topic_title, "text": obj.text,
                "status": obj.status, "topic_id": obj.topic_id,
                "responsible_name": obj.responsible_name,
            }
            AuditEvent.objects.create(
                actor=request.user, meeting=obj.meeting, action="updated",
                summary=f"Protokollkorrektur für „{obj.topic_title}“ am {obj.meeting.date:%d.%m.%Y}",
                changes={
                    "Protokollkorrektur": {
                        "Begründung": form.cleaned_data["correction_reason"],
                        "vorher": before, "nachher": after,
                    }
                },
            )


class TopicAttachmentAdmin(admin.ModelAdmin):
    list_display = ("label", "topic", "added_at")
    search_fields = ("label", "topic__title")


admin.site.register(AgendaItem, AgendaItemAdmin)
admin.site.register(TopicSnapshot, TopicSnapshotAdmin)
admin.site.register(TopicAttachment, TopicAttachmentAdmin)


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
        sync_admin_access(user, form.cleaned_data.get("is_administrator", False))


admin.site.unregister(User)
admin.site.unregister(Group)
admin.site.register(User, MeetingUserAdmin)
admin.site.register(Group, MeetingGroupAdmin)


@admin.register(OrganizationSettings)
class OrganizationSettingsAdmin(admin.ModelAdmin):
    list_display = ("name",)
    fields = ("name", "short_name", "timezone", "attachment_max_size_mb", ("primary_color", "primary_color_light", "primary_color_dark"), ("secondary_color", "secondary_color_light", "secondary_color_dark"), ("tertiary_color", "tertiary_color_light", "tertiary_color_dark"))

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == "timezone":
            return forms.ChoiceField(
                label=db_field.verbose_name,
                help_text=db_field.help_text,
                required=not db_field.blank,
                choices=[(zone, zone) for zone in sorted(available_timezones())],
            )
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        if db_field.name.endswith("_color") or db_field.name.endswith("_color_light") or db_field.name.endswith("_color_dark"):
            defaults = {
                "primary_color": "#00549F", "primary_color_light": "#00549F", "primary_color_dark": "#00549F",
                "secondary_color": "#8FC5FF", "secondary_color_light": "#8FC5FF", "secondary_color_dark": "#8FC5FF",
                "tertiary_color": "#FFCC00", "tertiary_color_light": "#FFCC00", "tertiary_color_dark": "#FFCC00",
            }
            if formfield:
                formfield.widget.attrs.update({
                    "placeholder": defaults.get(db_field.name, "#RRGGBB"),
                    "pattern": r"^#[0-9A-Fa-f]{6}$" if db_field.name in ("primary_color", "secondary_color", "tertiary_color") else r"^$|^#[0-9A-Fa-f]{6}$",
                    "spellcheck": "false",
                })
        return formfield

    def has_add_permission(self, request):
        return super().has_add_permission(request) and not OrganizationSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
