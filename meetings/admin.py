from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import GroupAdmin as DjangoGroupAdmin, UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import Group

from .models import (
    MeetingSeries, Meeting, Topic, AgendaItem, TopicSnapshot, TopicAttachment,
    TopicTransferHistory, AuditEvent, TopicComment, SeriesAccess, UserProfile,
)

admin.site.site_header = "Meeting Manager – Verwaltung"
admin.site.site_title = "Meeting Manager"
admin.site.index_title = "Daten und Benutzer verwalten"


class MeetingInline(admin.TabularInline):
    model = Meeting
    extra = 0


class SeriesAccessInline(admin.TabularInline):
    model = SeriesAccess
    extra = 1


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    extra = 0
    max_num = 1
    can_delete = False
    fields = ("short_description",)


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
    list_display = ("user", "series")
    list_filter = ("series",)
    search_fields = ("user__username", "user__first_name", "user__last_name", "series__name")


class MeetingUserAdmin(DjangoUserAdmin):
    inlines = [UserProfileInline, SeriesAccessInline]

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        user = form.instance
        if not user.is_superuser and not user.groups.exists():
            user.groups.add(Group.objects.get(name="Nutzer*in"))
        should_be_staff = user.is_superuser or user.groups.filter(name="Admin").exists()
        if user.is_staff != should_be_staff:
            user.is_staff = should_be_staff
            user.save(update_fields=["is_staff"])


admin.site.unregister(get_user_model())
admin.site.unregister(Group)
admin.site.register(get_user_model(), MeetingUserAdmin)
admin.site.register(Group, DjangoGroupAdmin)
