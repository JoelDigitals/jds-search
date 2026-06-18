from django.db import models
from django.contrib.auth.models import User
from urllib.parse import urlparse
import secrets


class DomainVerification(models.Model):
    METHOD_CHOICES = [("dns", "DNS TXT Record"), ("meta", "Meta-Tag"), ("file", "HTML-Datei")]
    STATUS_CHOICES = [("pending", "Ausstehend"), ("verified", "Verifiziert"), ("rejected", "Abgelehnt")]

    domain = models.CharField(max_length=253, unique=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="verified_domains")
    method = models.CharField(max_length=10, choices=METHOD_CHOICES, default="dns")
    token = models.CharField(max_length=64, unique=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = "jds-verify-" + secrets.token_hex(20)
        super().save(*args, **kwargs)

    @property
    def dns_record(self):
        return f"jds-verification={self.token}"

    @property
    def meta_tag(self):
        return f'<meta name="jds-verify" content="{self.token}">'

    def __str__(self):
        return f"{self.domain} ({self.status})"


class SearchIndex(models.Model):
    url = models.URLField(unique=True)
    title = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    content = models.TextField(blank=True)
    category = models.CharField(max_length=100, default="Web")
    domain = models.CharField(max_length=253, blank=True, db_index=True)
    is_verified = models.BooleanField(default=False, db_index=True)
    page_rank = models.FloatField(default=0.0)
    indexed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-indexed_at"]
        indexes = [models.Index(fields=["domain"]), models.Index(fields=["category"])]

    def save(self, *args, **kwargs):
        if not self.domain and self.url:
            self.domain = urlparse(self.url).netloc
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class CrawlQueue(models.Model):
    STATUS_CHOICES = [("pending", "Wartend"), ("crawling", "In Arbeit"), ("done", "Erledigt"), ("failed", "Fehler")]

    url = models.URLField(max_length=2000)
    priority = models.IntegerField(default=2)  # 1-4
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending", db_index=True)
    domain = models.CharField(max_length=253, blank=True, db_index=True)
    depth = models.IntegerField(default=0)
    retries = models.IntegerField(default=0)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-priority", "created_at"]

    def save(self, *args, **kwargs):
        if not self.domain and self.url:
            self.domain = urlparse(self.url).netloc
        super().save(*args, **kwargs)

    def __str__(self):
        return f"[P{self.priority}] {self.url}"


class CrawlLog(models.Model):
    url = models.URLField(max_length=2000)
    status_code = models.IntegerField(null=True)
    pages_indexed = models.IntegerField(default=0)
    pages_queued = models.IntegerField(default=0)
    duration_ms = models.IntegerField(default=0)
    error = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class SearchQuery(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="search_history")
    query = models.CharField(max_length=500)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    results_count = models.PositiveIntegerField(default=0)
    searched_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-searched_at"]
        verbose_name_plural = "Search queries"

    def __str__(self):
        return self.query


class AdCampaign(models.Model):
    advertiser = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ad_campaigns")
    title = models.CharField(max_length=200)
    description = models.TextField(max_length=500)
    target_url = models.URLField()
    budget = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    cost_per_click = models.DecimalField(max_digits=8, decimal_places=2, default=0.10)
    clicks = models.PositiveIntegerField(default=0)
    impressions = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def remaining_budget(self):
        spent = self.clicks * self.cost_per_click
        return max(self.budget - spent, 0)


class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="wallet")
    balance = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.user.username}: {self.balance} EUR"

    def charge(self, amount):
        from decimal import Decimal
        amount = Decimal(str(amount))
        if self.balance >= amount:
            self.balance -= amount
            self.save()
            return True
        return False
