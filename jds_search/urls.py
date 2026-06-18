from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
    path("search/", include("search.urls")),
    path("jdai/", include("jdai.urls")),
    path("mail/", include("mail_app.urls")),
    path("planner/", include("planner.urls")),
    path("marketplace/", include("marketplace.urls")),
    path("insights/", include("insights.urls")),
    path("present/", include("present.urls")),
    path("notes/", include("notes.urls")),
    path("api/", include("api.urls")),
]
