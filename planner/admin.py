from django.contrib import admin
from .models import Calendar, Event


@admin.register(Calendar)
class CalendarAdmin(admin.ModelAdmin):
    list_display = ["name", "user", "color"]


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ["title", "calendar", "start_time", "end_time", "all_day"]
    list_filter = ["all_day", "calendar"]
    search_fields = ["title", "description", "location"]
