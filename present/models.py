from django.db import models
from django.contrib.auth.models import User


class BusinessProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    business_name = models.CharField(max_length=300)
    slogan = models.CharField(max_length=500, blank=True)
    description = models.TextField(blank=True)
    logo_url = models.URLField(blank=True)
    website = models.URLField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    service_area = models.CharField(max_length=500, blank=True, help_text="z.B. Berlin, Brandenburg, deutschlandweit")
    opening_hours = models.TextField(blank=True, help_text="Mo-Fr: 9-18 Uhr, Sa: 10-14 Uhr")
    special_hours = models.TextField(blank=True, help_text="Feiertage, Sonderzeiten")
    category = models.CharField(max_length=200, blank=True, help_text="z.B. Restaurant, Arzt, Handwerker")
    inquiry_url = models.URLField(blank=True, help_text="Link zum Kontakt-/Anfrageformular")
    tags = models.CharField(max_length=500, blank=True, help_text="Kommagetrennt: handwerk, notdienst, 24h")
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def average_rating(self):
        avg = self.reviews.aggregate(models.Avg("rating"))["rating__avg"]
        return round(avg, 1) if avg else 0

    def review_count(self):
        return self.reviews.count()

    def is_open_now(self):
        from datetime import datetime
        now = datetime.now()
        weekday = now.weekday()
        hour = now.hour
        if not self.opening_hours:
            return None
        oh = self.opening_hours.lower()
        days = ["mo", "di", "mi", "do", "fr", "sa", "so"]
        day_short = days[weekday]
        for line in oh.split("\n"):
            line = line.strip()
            if line.startswith(day_short) or line.startswith(days[weekday]):
                if "-" in line:
                    times = line.split(":")[-1].strip() if ":" in line else line.split(" ", 1)[-1].strip()
                    parts = times.replace("uhr", "").replace(" ", "").split("-")
                    if len(parts) == 2:
                        try:
                            open_h = int(parts[0].split(":")[0])
                            close_h = int(parts[1].split(":")[0])
                            return open_h <= hour < close_h
                        except ValueError:
                            pass
        return None

    def __str__(self):
        return self.business_name


class BusinessService(models.Model):
    profile = models.ForeignKey(
        BusinessProfile, on_delete=models.CASCADE, related_name="services"
    )
    name = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    image_url = models.URLField(blank=True)

    def __str__(self):
        return self.name


class BusinessReview(models.Model):
    profile = models.ForeignKey(
        BusinessProfile, on_delete=models.CASCADE, related_name="reviews"
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.author} - {self.rating}★"
