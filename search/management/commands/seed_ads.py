from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from search.models import AdCampaign, Wallet


class Command(BaseCommand):
    help = "Erstellt Beispiel-Werbekampagnen mit Guthaben"

    def handle(self, *args, **kwargs):
        user = User.objects.filter(username="JoelDigitals").first()
        if not user:
            self.stdout.write("Admin nicht gefunden.")
            return

        w, _ = Wallet.objects.get_or_create(user=user)
        if w.balance < 50:
            w.balance = 100
            w.save()

        campaigns = [
            {"title": "JDS Marketplace – Jetzt verkaufen!", "description": "Stelle deine Produkte ein und erreiche tausende Kunden.", "target_url": "/marketplace/", "budget": 20, "cost_per_click": 0.10},
            {"title": "JDAI – Dein KI-Assistent", "description": "Die intelligente KI fur deinen Alltag. Jetzt ausprobieren.", "target_url": "/jdai/", "budget": 15, "cost_per_click": 0.10},
        ]

        for c in campaigns:
            AdCampaign.objects.get_or_create(advertiser=user, title=c["title"], defaults=c)

        count = AdCampaign.objects.filter(advertiser=user, is_active=True).count()
        self.stdout.write(self.style.SUCCESS(f"[OK] {count} Kampagnen aktiv, Guthaben: {w.balance} EUR"))
