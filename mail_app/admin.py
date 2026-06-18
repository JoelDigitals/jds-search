from django.contrib import admin
from .models import Email, UserEmail


@admin.register(UserEmail)
class UserEmailAdmin(admin.ModelAdmin):
    list_display = ["user", "address"]
    search_fields = ["address", "user__username"]


@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    list_display = ["subject", "sender", "recipient", "folder", "is_read", "created_at"]
    list_filter = ["folder", "is_read", "is_starred"]
    search_fields = ["subject", "body", "sender", "recipient"]
