from django.db import models
from django.contrib.auth.models import User


class Calendar(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="calendars")
    name = models.CharField(max_length=200)
    color = models.CharField(max_length=7, default="#4285f4")

    def __str__(self):
        return self.name


class Event(models.Model):
    calendar = models.ForeignKey(
        Calendar, on_delete=models.CASCADE, related_name="events"
    )
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=500, blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    all_day = models.BooleanField(default=False)
    color = models.CharField(max_length=7, default="#4285f4")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["start_time"]

    def __str__(self):
        return self.title
