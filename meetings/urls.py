from django.urls import path
from . import views
urlpatterns = [
 path("login/",views.login_view,name="login"), path("logout/",views.logout_view,name="logout"),
 path("",views.dashboard,name="dashboard"), path("meeting/<int:pk>/",views.meeting_detail,name="meeting"),
 path("meeting/<int:pk>/protocol/",views.protocol,name="protocol"), path("meeting/<int:pk>/finalize/",views.finalize,name="finalize"),
 path("topics/new/",views.topic_new,name="topic_new"), path("topics/<int:pk>/",views.topic_edit,name="topic_edit"),
 path("topics/<int:pk>/attachments/add/",views.attachment_add,name="attachment_add"),
 path("admin/series/",views.series_admin,name="series_admin"),
]
