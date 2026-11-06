from django.contrib import admin
from .models import MeetingSeries, Meeting, Topic, AgendaItem, TopicSnapshot, TopicAttachment, TopicTransferHistory, AuditEvent

class MeetingInline(admin.TabularInline):
    model = Meeting
    extra = 0

@admin.register(MeetingSeries)
class SeriesAdmin(admin.ModelAdmin):
    list_display = ("name", "recurrence", "active", "start_date", "end_date")
    inlines = [MeetingInline]

@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ("series", "date", "finalized_at")
    list_filter = ("series", "finalized_at")

@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ("title", "series", "due_date", "status")
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
