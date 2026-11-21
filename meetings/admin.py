from django import forms
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import (
    GroupAdmin as DjangoGroupAdmin,
    UserAdmin as DjangoUserAdmin,
    UserChangeForm as DjangoUserChangeForm,
)
from django.contrib.auth.models import Group

from .models import (
    MeetingSeries, Meeting, Topic, AgendaItem, TopicSnapshot, TopicAttachment,
    TopicTransferHistory, AuditEvent, TopicComment, SeriesAccess, UserProfile,
)
from .user_display import user_display_name

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
    fields = ("user", "series", "role")
    autocomplete_fields = ("user", "series")


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
    list_display = ("title", "series", "due_date", "assigned_to", "status")
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
        return user_display_name(obj.user)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        field = super().formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name == "user":
            field.label_from_instance = user_display_name
        return field


class MeetingUserChangeForm(DjangoUserChangeForm):
    short_description = forms.CharField(
        label="Kurzbeschreibung", required=False, max_length=80,
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
        if "groups" in self.fields:
            self.fields["groups"].queryset = Group.objects.filter(name="Admin")

class MeetingUserAdmin(DjangoUserAdmin):
    form = MeetingUserChangeForm
    inlines = [SeriesAccessInline]
    list_display = ("username", "display_name", "email", "is_staff", "is_active")
    fieldsets = (
        ("Persönliche Informationen", {
            "fields": ("username", "first_name", "last_name", "email", "short_description"),
        }),
        ("Berechtigungen", {
            "fields": ("is_active", "groups", "is_superuser"),
        }),
        ("Wichtige Daten", {
            "fields": ("last_login", "date_joined"),
        }),
    )
    readonly_fields = ("last_login", "date_joined")
    filter_horizontal = ("groups",)

    @admin.display(description="Anzeigename")
    def display_name(self, obj):
        return user_display_name(obj)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        user = form.instance
        should_be_staff = user.is_superuser or user.groups.filter(name="Admin").exists()
        if user.is_staff != should_be_staff:
            user.is_staff = should_be_staff
            user.save(update_fields=["is_staff"])


admin.site.unregister(User)
admin.site.unregister(Group)
admin.site.register(User, MeetingUserAdmin)
admin.site.register(Group, DjangoGroupAdmin)
