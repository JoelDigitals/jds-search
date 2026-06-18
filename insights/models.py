from django.db import models


class AnalyticsSnapshot(models.Model):
    date = models.DateField(unique=True)
    searches = models.PositiveIntegerField(default=0)
    page_views = models.PositiveIntegerField(default=0)
    mails_sent = models.PositiveIntegerField(default=0)
    events_created = models.PositiveIntegerField(default=0)
    products_listed = models.PositiveIntegerField(default=0)
    ai_chats = models.PositiveIntegerField(default=0)
    new_users = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return str(self.date)
