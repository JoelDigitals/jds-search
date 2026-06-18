from django.contrib import admin
from .models import BusinessProfile, BusinessService, BusinessReview


class BusinessServiceInline(admin.TabularInline):
    model = BusinessService
    extra = 1


class BusinessReviewInline(admin.TabularInline):
    model = BusinessReview
    extra = 0


@admin.register(BusinessProfile)
class BusinessProfileAdmin(admin.ModelAdmin):
    list_display = ["business_name", "user", "is_published", "created_at"]
    list_filter = ["is_published"]
    search_fields = ["business_name", "description"]
    inlines = [BusinessServiceInline, BusinessReviewInline]
