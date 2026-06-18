from django.contrib import admin
from .models import AnalyticsSnapshot


@admin.register(AnalyticsSnapshot)
class AnalyticsSnapshotAdmin(admin.ModelAdmin):
    list_display = ["date", "searches", "page_views", "mails_sent", "new_users"]
    list_filter = ["date"]
