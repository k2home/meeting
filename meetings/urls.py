from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("", views.dashboard, name="dashboard"),
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
    path("admin/series/", views.series_admin, name="series_admin"),
]
