from django.db import models
from django.contrib.auth.models import User


class UserEmail(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="email_address")
    address = models.EmailField(unique=True)

    def save(self, *args, **kwargs):
        if not self.address:
            self.address = f"{self.user.username.lower()}@jds-search.de"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.address


class Email(models.Model):
    FOLDER_CHOICES = [
        ("inbox", "Posteingang"),
        ("sent", "Gesendet"),
        ("draft", "Entwürfe"),
        ("trash", "Papierkorb"),
        ("archive", "Archiv"),
        ("spam", "Spam"),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="emails")
    sender = models.EmailField()
    recipient = models.EmailField()
    subject = models.CharField(max_length=500)
    body = models.TextField(blank=True)
    folder = models.CharField(max_length=20, choices=FOLDER_CHOICES, default="inbox")
    is_read = models.BooleanField(default=False)
    is_starred = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.subject
