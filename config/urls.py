from django.contrib import admin
from django.urls import path, include
from django.conf import settings
import os
from django.conf.urls.static import static
urlpatterns = [
    *([path("django-admin/", admin.site.urls)] if os.path.isfile("/var/lib/meeting-manager-updater/testing-mode") else []),
    path("", include("meetings.urls")),
] + (static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) if settings.DEBUG else [])
