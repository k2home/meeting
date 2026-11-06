from django.urls import path
from . import views, user_views

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("", views.dashboard, name="dashboard"),
    path("calendar/", views.calendar_view, name="calendar"),
    path("calendar/meeting/<int:pk>/edit/", views.meeting_date_edit, name="meeting_date_edit"),
    path("calendar/meeting/<int:pk>/delete/", views.meeting_delete, name="meeting_delete"),
    path("meeting/<int:pk>/", views.meeting_detail, name="meeting"),
    path("meeting/<int:pk>/protocol/", views.protocol, name="protocol"),
    path("meeting/<int:pk>/finalize/", views.finalize, name="finalize"),
    path("topics/new/", views.topic_new, name="topic_new"),
    path("topics/<int:pk>/", views.topic_edit, name="topic_edit"),
    path("topics/<int:pk>/archive/", views.topic_archive, name="topic_archive"),
    path("topics/<int:pk>/reopen/", views.topic_reopen, name="topic_reopen"),
    path("topics/<int:pk>/transfer/", views.topic_transfer, name="topic_transfer"),
    path("topics/<int:pk>/attachments/add/", views.attachment_add, name="attachment_add"),
    path("archive/", views.archive, name="archive"),
    path("admin/series/", views.series_admin, name="series_admin"),\n    path("admin/users/", user_views.user_list, name="user_list"),\n    path("admin/users/new/", user_views.user_create, name="user_create"),\n    path("admin/users/<int:pk>/edit/", user_views.user_edit, name="user_edit"),\n    path("admin/users/<int:pk>/password/", user_views.user_password, name="user_password"),
]
