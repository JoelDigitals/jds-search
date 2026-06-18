from django.contrib import admin
from .models import SearchIndex, SearchQuery, AdCampaign, DomainVerification, CrawlQueue, CrawlLog, Wallet


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ["user", "balance"]
    search_fields = ["user__username"]


@admin.register(DomainVerification)
class DomainVerificationAdmin(admin.ModelAdmin):
    list_display = ["domain", "owner", "method", "status", "created_at"]
    list_filter = ["status", "method"]
    search_fields = ["domain"]
    readonly_fields = ["token", "dns_record", "meta_tag"]
    actions = ["verify_domains"]

    def verify_domains(self, request, queryset):
        from django.utils import timezone
        updated = queryset.filter(status="pending").update(status="verified", verified_at=timezone.now())
        self.message_user(request, f"{updated} Domains verifiziert.")
    verify_domains.short_description = "Ausgewählte Domains verifizieren"


@admin.register(SearchIndex)
class SearchIndexAdmin(admin.ModelAdmin):
    list_display = ["title", "domain", "category", "is_verified", "indexed_at"]
    list_filter = ["category", "is_verified"]
    search_fields = ["title", "description", "url", "domain"]
    list_per_page = 50
    ordering = ["-indexed_at"]


@admin.register(CrawlQueue)
class CrawlQueueAdmin(admin.ModelAdmin):
    list_display = ["url", "domain", "priority", "status", "retries", "created_at"]
    list_filter = ["status", "priority"]
    search_fields = ["url", "domain"]
    list_per_page = 50


@admin.register(CrawlLog)
class CrawlLogAdmin(admin.ModelAdmin):
    list_display = ["url", "status_code", "pages_indexed", "duration_ms", "created_at"]
    list_per_page = 50


@admin.register(SearchQuery)
class SearchQueryAdmin(admin.ModelAdmin):
    list_display = ["query", "results_count", "searched_at"]
    search_fields = ["query"]
    list_per_page = 50


@admin.register(AdCampaign)
class AdCampaignAdmin(admin.ModelAdmin):
    list_display = ["title", "advertiser", "clicks", "impressions", "is_active"]
    list_filter = ["is_active"]
