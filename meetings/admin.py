from django.contrib import admin
from .models import MeetingSeries, Meeting, Topic, AgendaItem, TopicSnapshot, TopicAttachment
class MeetingInline(admin.TabularInline):
    model = Meeting
    extra = 0
@admin.register(MeetingSeries)
class SeriesAdmin(admin.ModelAdmin):
    list_display = ("name","recurrence","active","start_date","end_date")
    inlines = [MeetingInline]
@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ("series","date","finalized_at")
    list_filter = ("series","finalized_at")
@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ("title","series","due_date","status")
    list_filter = ("series","status")
    search_fields = ("title","description")
admin.site.register(AgendaItem)
admin.site.register(TopicSnapshot)
admin.site.register(TopicAttachment)
