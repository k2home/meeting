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
    list_display = ("display_user", "series")
    list_filter = ("series",)
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
    series_access = forms.ModelMultipleChoiceField(
        label="Serienberechtigungen",
        queryset=MeetingSeries.objects.all(),
        required=False,
        widget=admin.widgets.FilteredSelectMultiple("Besprechungsreihen", is_stacked=False),
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
            self.fields["series_access"].initial = MeetingSeries.objects.filter(
                user_access__user=self.instance
            )
        self.fields["is_superuser"].label = "Django-Superuser"

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            self.save_extra_fields()
        return user

    def save_extra_fields(self):
        if not self.instance.pk:
            return
        UserProfile.objects.update_or_create(
            user=self.instance,
            defaults={"short_description": self.cleaned_data["short_description"]},
        )
        SeriesAccess.objects.filter(user=self.instance).exclude(
            series__in=self.cleaned_data["series_access"]
        ).delete()
        existing_ids = set(
            SeriesAccess.objects.filter(user=self.instance).values_list("series_id", flat=True)
        )
        SeriesAccess.objects.bulk_create([
            SeriesAccess(user=self.instance, series=series)
            for series in self.cleaned_data["series_access"]
            if series.pk not in existing_ids
        ])


class MeetingUserAdmin(DjangoUserAdmin):
    form = MeetingUserChangeForm
    inlines = []
    list_display = ("username", "display_name", "email", "is_staff", "is_active")
    fieldsets = (
        ("Persönliche Informationen", {
            "fields": ("username", "first_name", "last_name", "email", "short_description"),
        }),
        ("Berechtigungen", {
            "fields": ("is_active", "groups", "is_superuser"),
        }),
        ("Serienberechtigungen", {
            "fields": ("series_access",),
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
        form.save_extra_fields()
        user = form.instance
        if not user.is_superuser and not user.groups.exists():
            user.groups.add(Group.objects.get(name="Nutzer*in"))
        should_be_staff = user.is_superuser or user.groups.filter(name="Admin").exists()
        if user.is_staff != should_be_staff:
            user.is_staff = should_be_staff
            user.save(update_fields=["is_staff"])


admin.site.unregister(User)
admin.site.unregister(Group)
admin.site.register(User, MeetingUserAdmin)
admin.site.register(Group, DjangoGroupAdmin)
