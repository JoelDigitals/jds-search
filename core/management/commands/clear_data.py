from django.core.management.base import BaseCommand
from search.models import SearchIndex, SearchQuery, AdCampaign
from mail_app.models import Email
from marketplace.models import Product, Category, Cart, CartItem
from planner.models import Event, Calendar
from notes.models import Note
from jdai.models import ChatSession, ChatMessage


class Command(BaseCommand):
    help = "Löscht alle Nutzerdaten und hält nur den Admin"

    def handle(self, *args, **options):
        models = [
            (SearchIndex, "Suchindex"),
            (SearchQuery, "Suchverlauf"),
            (AdCampaign, "Werbeanzeigen"),
            (Email, "E-Mails"),
            (Product, "Produkte"),
            (Category, "Kategorien"),
            (Cart, "Warenkörbe"),
            (CartItem, "Warenkorb-Items"),
            (Event, "Termine"),
            (Calendar, "Kalender"),
            (Note, "Notizen"),
            (ChatSession, "Chats"),
            (ChatMessage, "Chat-Nachrichten"),
        ]

        self.stdout.write(self.style.MIGRATE_HEADING("=== Lösche alle Daten ==="))

        for model, name in models:
            count = model.objects.count()
            model.objects.all().delete()
            self.stdout.write(f"  [OK] {count} {name} gelöscht")

        self.stdout.write(self.style.SUCCESS("\nAlle Daten gelöscht. Datenbank ist frisch."))
        self.stdout.write("  python manage.py crawl <url> --depth 2  -> Seiten indexieren")
        self.stdout.write("  python manage.py seed-admin              -> Nur Admin anlegen")
