from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("", views.dashboard, name="dashboard"),
    path("my-tasks/", views.my_tasks, name="my_tasks"),
    path("meeting/<int:pk>/", views.meeting_detail, name="meeting"),
    path("meeting/<int:pk>/agenda/reorder/", views.agenda_reorder, name="agenda_reorder"),
    path("meeting/<int:pk>/protocol/", views.protocol, name="protocol"),
    path("meeting/<int:pk>/protocol/pdf/", views.protocol_pdf, name="protocol_pdf"),
    path("meeting/<int:pk>/protocol/word/", views.protocol_docx, name="protocol_docx"),
    path("meeting/<int:pk>/finalize/", views.finalize, name="finalize"),
    path("topics/new/", views.topic_new, name="topic_new"),
    path("topics/<int:pk>/", views.topic_edit, name="topic_edit"),
    path("topics/<int:pk>/comments/add/", views.topic_comment_add, name="topic_comment_add"),
    path("topics/<int:pk>/archive/", views.topic_archive, name="topic_archive"),
    path("topics/<int:pk>/reopen/", views.topic_reopen, name="topic_reopen"),
    path("topics/<int:pk>/transfer/", views.topic_transfer, name="topic_transfer"),
    path("topics/<int:pk>/attachments/add/", views.attachment_add, name="attachment_add"),
    path("archive/", views.archive, name="archive"),
    path("history/", views.audit_history, name="audit_history"),
    path("admin/series/", views.series_admin, name="series_admin"),
    path("admin/series/<int:pk>/edit/", views.series_edit, name="series_edit"),
    path("admin/series/<int:pk>/delete/", views.series_delete, name="series_delete"),
    path("admin/meeting/<int:pk>/edit/", views.meeting_edit, name="meeting_edit"),
    path("admin/meeting/<int:pk>/delete/", views.meeting_delete, name="meeting_delete"),
]
