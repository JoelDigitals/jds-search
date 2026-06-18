from django.contrib import admin
from .models import APIKey, APIRateLimit


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ["name", "user", "prefix", "is_active", "request_count", "last_used"]
    list_filter = ["is_active"]
    readonly_fields = ["key_hash", "prefix"]
