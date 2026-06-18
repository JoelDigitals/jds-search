import secrets
import hashlib
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class APIKey(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="api_keys")
    name = models.CharField(max_length=200, default="Default")
    key_hash = models.CharField(max_length=128, unique=True)
    prefix = models.CharField(max_length=12)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(null=True, blank=True)
    request_count = models.PositiveIntegerField(default=0)

    @staticmethod
    def generate():
        key = "jds_" + secrets.token_hex(24)
        return key, hashlib.sha256(key.encode()).hexdigest(), key[:10]

    def __str__(self):
        return f"{self.name} ({self.prefix}...)"

    def log_use(self):
        self.last_used = timezone.now()
        self.request_count += 1
        self.save(update_fields=["last_used", "request_count"])


class APIRateLimit(models.Model):
    api_key = models.ForeignKey(APIKey, on_delete=models.CASCADE, related_name="rate_limits")
    endpoint = models.CharField(max_length=200)
    count = models.PositiveIntegerField(default=0)
    window_start = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["api_key", "endpoint"]
