from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from search.models import SearchIndex
from mail_app.models import Email
from marketplace.models import Category, Product
from planner.models import Calendar, Event
from datetime import datetime, timedelta
from django.utils import timezone


class Command(BaseCommand):
    help = "Seedet die Datenbank mit Beispiel-Daten"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.MIGRATE_HEADING("=== JDS Database Seed ==="))

        # User
        if not User.objects.filter(username="JoelDigitals").exists():
            User.objects.create_superuser("JoelDigitals", "admin@jds-search.de", "Jo240207!")
            self.stdout.write("  [OK] Superuser 'JoelDigitals' erstellt")
        if not User.objects.filter(username="joel").exists():
            User.objects.create_superuser("joel", "joel@jds.com", "admin123")

        user = User.objects.get(username="JoelDigitals")

        # Search Index
        SearchIndex.objects.all().delete()
        pages = [
            {
                "url": "https://www.python.org",
                "title": "Python Programming Language",
                "description": "Python ist eine interpretierte, objektorientierte Programmiersprache. Offizielle Website mit Downloads und Dokumentation.",
                "category": "Programmierung",
            },
            {
                "url": "https://www.djangoproject.com",
                "title": "Django – The Web framework for perfectionists",
                "description": "Django ist ein High-Level Python Web-Framework für schnelle Entwicklung und sauberes Design.",
                "category": "Programmierung",
            },
            {
                "url": "https://de.wikipedia.org/wiki/Deutschland",
                "title": "Deutschland – Wikipedia",
                "description": "Deutschland ist ein Bundesstaat in Mitteleuropa mit 16 Bundesländern und ca. 84 Millionen Einwohnern.",
                "category": "Wissen",
            },
            {
                "url": "https://www.jds-search.com",
                "title": "JDS Search – Deine Suchmaschine",
                "description": "JDS Search ist eine intelligente Suchmaschine von Joel Digital Systems.",
                "category": "JDS",
            },
            {
                "url": "https://www.openai.com",
                "title": "OpenAI – Creating safe AI",
                "description": "OpenAI ist ein KI-Forschungsunternehmen, das künstliche Intelligenz entwickelt und erforscht.",
                "category": "KI",
            },
            {
                "url": "https://www.github.com",
                "title": "GitHub – Where the world builds software",
                "description": "GitHub ist die weltweit größte Plattform für Softwareentwicklung und Versionskontrolle.",
                "category": "Programmierung",
            },
            {
                "url": "https://de.wikipedia.org/wiki/Künstliche_Intelligenz",
                "title": "Künstliche Intelligenz – Wikipedia",
                "description": "Künstliche Intelligenz (KI) ist ein Teilgebiet der Informatik, das sich mit der Automatisierung intelligenten Verhaltens befasst.",
                "category": "KI",
            },
            {
                "url": "https://www.amazon.de",
                "title": "Amazon.de – Online Shopping",
                "description": "Amazon.de bietet Millionen von Produkten mit schneller Lieferung. Der größte Online-Marktplatz Deutschlands.",
                "category": "Shopping",
            },
            {
                "url": "https://www.netflix.com",
                "title": "Netflix – Filme & Serien streamen",
                "description": "Netflix ist ein Streaming-Dienst mit einer großen Auswahl an Serien, Filmen und Dokumentationen.",
                "category": "Entertainment",
            },
            {
                "url": "https://www.spotify.com",
                "title": "Spotify – Musik und Podcasts",
                "description": "Spotify ist ein Musik-Streaming-Dienst mit Millionen von Songs und Podcasts.",
                "category": "Entertainment",
            },
            {
                "url": "https://www.stackoverflow.com",
                "title": "Stack Overflow – Where Developers Learn",
                "description": "Stack Overflow ist die größte Frage-Antwort-Plattform für Entwickler.",
                "category": "Programmierung",
            },
            {
                "url": "https://de.wikipedia.org/wiki/Berlin",
                "title": "Berlin – Wikipedia",
                "description": "Berlin ist die Hauptstadt und ein Land der Bundesrepublik Deutschland. Mit 3,7 Mio. Einwohnern die größte deutsche Stadt.",
                "category": "Wissen",
            },
            {
                "url": "https://www.jds-search.com/jdai",
                "title": "JDAI – Dein KI-Assistent",
                "description": "JDAI ist der persönliche KI-Assistent von Joel Digital Systems. Hilft bei Fragen, Terminen und mehr.",
                "category": "JDS",
            },
            {
                "url": "https://www.jds-search.com/marketplace",
                "title": "JDS Marketplace – Online Marktplatz",
                "description": "Auf dem JDS Marketplace kannst du Produkte kaufen und verkaufen. Der Marktplatz von JDS.",
                "category": "JDS",
            },
            {
                "url": "https://www.google.com",
                "title": "Google",
                "description": "Google ist eine weltweit führende Suchmaschine und Technologieunternehmen.",
                "category": "Web",
            },
            {
                "url": "https://de.wikipedia.org/wiki/HTML",
                "title": "HTML – Wikipedia",
                "description": "Hypertext Markup Language (HTML) ist die textbasierte Auszeichnungssprache für Webseiten.",
                "category": "Programmierung",
            },
            {
                "url": "https://de.wikipedia.org/wiki/CSS",
                "title": "CSS – Wikipedia",
                "description": "Cascading Style Sheets (CSS) ist eine Stylesheet-Sprache für die Gestaltung von Webdokumenten.",
                "category": "Programmierung",
            },
            {
                "url": "https://de.wikipedia.org/wiki/JavaScript",
                "title": "JavaScript – Wikipedia",
                "description": "JavaScript ist eine Skriptsprache für dynamische Webinhalte und wird in über 97% aller Websites eingesetzt.",
                "category": "Programmierung",
            },
            {
                "url": "https://de.wikipedia.org/wiki/Datenschutz",
                "title": "Datenschutz – Wikipedia",
                "description": "Datenschutz bezeichnet den Schutz personenbezogener Daten vor Missbrauch und unbefugter Verarbeitung.",
                "category": "Wissen",
            },
            {
                "url": "https://de.wikipedia.org/wiki/Verschlüsselung",
                "title": "Verschlüsselung – Wikipedia",
                "description": "Verschlüsselung ist die Umwandlung von Daten in eine nicht lesbare Form zum Schutz vor unbefugtem Zugriff.",
                "category": "Wissen",
            },
            {
                "url": "https://www.microsoft.com",
                "title": "Microsoft – Official Website",
                "description": "Microsoft Corporation ist ein US-amerikanischer Softwarehersteller. Bekannt für Windows, Office und Azure.",
                "category": "Technologie",
            },
            {
                "url": "https://www.apple.com",
                "title": "Apple",
                "description": "Apple Inc. entwickelt iPhone, Mac, iPad, Apple Watch und ist ein führendes Technologieunternehmen.",
                "category": "Technologie",
            },
            {
                "url": "https://de.wikipedia.org/wiki/Internet",
                "title": "Internet – Wikipedia",
                "description": "Das Internet ist ein weltweiter Verbund von Rechnernetzwerken zum Austausch von Daten.",
                "category": "Wissen",
            },
            {
                "url": "https://de.wikipedia.org/wiki/Cloud_Computing",
                "title": "Cloud Computing – Wikipedia",
                "description": "Cloud Computing bezeichnet die Bereitstellung von IT-Ressourcen über das Internet.",
                "category": "Technologie",
            },
            {
                "url": "https://www.jds-search.com/translate",
                "title": "JDS Translate – Übersetzungsdienst",
                "description": "JDS Translate übersetzt Texte zwischen 11 Sprachen. Live-Übersetzung mit Sprachausgabe.",
                "category": "JDS",
            },
            {
                "url": "https://www.jds-search.com/maps",
                "title": "JDS Maps – Interaktive Karten",
                "description": "JDS Maps bietet interaktive Karten mit Standorten in ganz Deutschland.",
                "category": "JDS",
            },
            {
                "url": "https://www.jds-search.com/notes",
                "title": "JDS Notizen – Deine digitale Notiz-App",
                "description": "JDS Notizen ist eine Keep-ähnliche App für farbige Karteikarten, Pins und Archivierung.",
                "category": "JDS",
            },
            {
                "url": "https://de.wikipedia.org/wiki/DSGVO",
                "title": "Datenschutz-Grundverordnung – Wikipedia",
                "description": "Die DSGVO ist eine EU-Verordnung zum Schutz personenbezogener Daten. Gültig seit Mai 2018.",
                "category": "Wissen",
            },
            {
                "url": "https://de.wikipedia.org/wiki/Kryptographie",
                "title": "Kryptographie – Wikipedia",
                "description": "Kryptographie ist die Wissenschaft der Verschlüsselung von Informationen zum Schutz vor unbefugtem Zugriff.",
                "category": "Wissen",
            },
            {
                "url": "https://www.nodejs.org",
                "title": "Node.js – JavaScript Runtime",
                "description": "Node.js ist eine plattformübergreifende JavaScript-Laufzeitumgebung für serverseitige Anwendungen.",
                "category": "Programmierung",
            },
            {
                "url": "https://www.docker.com",
                "title": "Docker – Container Platform",
                "description": "Docker ist eine Open-Source-Software zur Container-Virtualisierung von Anwendungen.",
                "category": "Programmierung",
            },
            {
                "url": "https://de.wikipedia.org/wiki/Maschinelles_Lernen",
                "title": "Maschinelles Lernen – Wikipedia",
                "description": "Maschinelles Lernen ist ein Teilgebiet der KI, bei dem Computer aus Daten lernen.",
                "category": "KI",
            },
            {
                "url": "https://de.wikipedia.org/wiki/Blockchain",
                "title": "Blockchain – Wikipedia",
                "description": "Eine Blockchain ist eine dezentrale, fälschungssichere Datenstruktur für Transaktionen.",
                "category": "Technologie",
            },
            {
                "url": "https://www.zalando.de",
                "title": "Zalando – Schuhe & Mode online",
                "description": "Zalando ist ein deutscher Online-Versandhändler für Schuhe und Mode mit kostenlosem Versand.",
                "category": "Shopping",
            },
            {
                "url": "https://www.ebay.de",
                "title": "eBay Deutschland – Online Marktplatz",
                "description": "eBay ist ein weltweiter Online-Marktplatz für Privat- und Gewerbeverkäufer.",
                "category": "Shopping",
            },
            {
                "url": "https://de.wikipedia.org/wiki/Cybersicherheit",
                "title": "Cybersicherheit – Wikipedia",
                "description": "Cybersicherheit umfasst alle Maßnahmen zum Schutz von Computersystemen vor Angriffen und Datenverlust.",
                "category": "Wissen",
            },
            {
                "url": "https://www.adac.de",
                "title": "ADAC – Mobilität & Verkehr",
                "description": "Der ADAC ist der größte Automobilclub Europas mit Pannenhilfe, Reiseinformationen und Verkehrsservice.",
                "category": "Auto & Verkehr",
            },
            {
                "url": "https://www.tagesschau.de",
                "title": "tagesschau.de – Nachrichten",
                "description": "Die Tagesschau ist die älteste und meistgesehene Nachrichtensendung im deutschen Fernsehen.",
                "category": "News",
            },
            {
                "url": "https://www.spiegel.de",
                "title": "DER SPIEGEL – Nachrichten",
                "description": "Spiegel Online ist das führende deutsche Nachrichtenmagazin mit Investigativjournalismus.",
                "category": "News",
            },
            {
                "url": "https://www.bundesregierung.de",
                "title": "Bundesregierung – Startseite",
                "description": "Offizielle Website der deutschen Bundesregierung mit aktuellen Informationen und Politik.",
                "category": "Regierung",
            },
            {
                "url": "https://de.wikipedia.org/wiki/Deutsche_Sprache",
                "title": "Deutsche Sprache – Wikipedia",
                "description": "Die deutsche Sprache ist eine westgermanische Sprache mit etwa 100 Millionen Muttersprachlern.",
                "category": "Wissen",
            },
            {
                "url": "https://www.youtube.com",
                "title": "YouTube – Videos ansehen",
                "description": "YouTube ist das weltweit größte Videoportal zum Hochladen und Ansehen von Videos.",
                "category": "Entertainment",
            },
            {
                "url": "https://www.jds-search.com/security",
                "title": "JDS Security – Ihre Daten sind sicher",
                "description": "JDS Security: TLS 1.3 Verschlüsselung, AES-256, DSGVO-konform. Ihre Privatsphäre ist unser Auftrag.",
                "category": "JDS",
            },
        ]
        for page_data in pages:
            SearchIndex.objects.create(**page_data)
        self.stdout.write(f"  [OK] {len(pages)} Seiten indexiert")

        # Mail
        Email.objects.all().delete()
        sample_mails = [
            {
                "user": user,
                "sender": "team@jds-search.com",
                "recipient": "joel@jds-mail.com",
                "subject": "Willkommen bei JDS!",
                "body": "Hallo Joel,\n\nwillkommen bei JDS – deinem digitalen Ökosystem!\n\nHier sind deine Zugangsdaten:\n- JDS Search: search.jds-search.com\n- JDAI: jdai.jds-search.com\n- JDS Mail: mail.jds-search.com\n\nViel Spaß!\nDein JDS-Team",
                "folder": "inbox",
                "is_read": False,
            },
            {
                "user": user,
                "sender": "noreply@jds-search.com",
                "recipient": "joel@jds-mail.com",
                "subject": "Deine JDS Marketplace Bestellung",
                "body": "Hallo Joel,\n\ndeine Bestellung #JDS-2024-001 wurde bestätigt.\n\nBestellte Artikel:\n- Python Buch für Einsteiger (29,99 €)\n- Django T-Shirt (24,99 €)\n\nGesamt: 54,98 €\n\nLieferung in 2-3 Werktagen.\n\nViele Grüße\nJDS Marketplace Team",
                "folder": "inbox",
                "is_read": True,
            },
            {
                "user": user,
                "sender": "joel@jds-mail.com",
                "recipient": "team@jds-search.com",
                "subject": "Feedback zum JDS System",
                "body": "Hallo Team,\n\nich bin begeistert vom JDS System! Besonders JDAI und JDS Search sind klasse.\n\nEin paar Verbesserungsvorschläge:\n1. Dark Mode wäre super\n2. Mehr Integrationen mit externen Diensten\n\nDanke für die tolle Arbeit!\nJoel",
                "folder": "sent",
                "is_read": True,
            },
            {
                "user": user,
                "sender": "newsletter@tech.com",
                "recipient": "joel@jds-mail.com",
                "subject": "Tech Weekly: KI Trends 2024",
                "body": "Die neuesten KI-Trends:\n\n1. Generative AI ist überall\n2. Edge Computing wächst\n3. Open Source KI-Modelle werden besser\n\nMehr dazu in unserem Blog!",
                "folder": "inbox",
                "is_read": False,
            },
            {
                "user": user,
                "sender": "kalender@jds-search.com",
                "recipient": "joel@jds-mail.com",
                "subject": "Erinnerung: Meeting morgen um 10:00",
                "body": "Hallo Joel,\n\ndies ist eine Erinnerung an dein morgiges Meeting:\n\nTitel: Sprint Review\nZeit: 10:00 - 11:00 Uhr\nOrt: Konferenzraum A\n\nBitte bereite deine Präsentation vor.\n\nViele Grüße\nJDS Planer",
                "folder": "inbox",
                "is_read": False,
            },
        ]
        for mail_data in sample_mails:
            Email.objects.create(**mail_data)
        self.stdout.write(f"  [OK] {len(sample_mails)} E-Mails erstellt")

        # Categories
        Category.objects.all().delete()
        categories = [
            ("Elektronik", "elektronik"),
            ("Kleidung", "kleidung"),
            ("Bücher", "buecher"),
            ("Haus & Garten", "haus-garten"),
            ("Sport", "sport"),
            ("Spielzeug", "spielzeug"),
            ("Auto & Motorrad", "auto-motorrad"),
            ("Software", "software"),
        ]
        for name, slug in categories:
            Category.objects.create(name=name, slug=slug)
        self.stdout.write(f"  [OK] {len(categories)} Kategorien erstellt")

        # Products
        Product.objects.all().delete()
        products = [
            {"name": "Python Buch für Einsteiger", "price": 29.99, "category": "buecher",
             "description": "Das ultimative Python-Buch für Programmieranfänger. Von Grundlagen bis zu fortgeschrittenen Themen."},
            {"name": "Django T-Shirt", "price": 24.99, "category": "kleidung",
             "description": "Stylisches T-Shirt mit Django-Logo. 100% Baumwolle, verschiedene Größen."},
            {"name": "Wireless Kopfhörer Pro", "price": 89.99, "category": "elektronik",
             "description": "Premium Bluetooth Kopfhörer mit Active Noise Cancelling. 30h Akkulaufzeit."},
            {"name": "Garten-Lounge-Set", "price": 499.00, "category": "haus-garten",
             "description": "Komfortables 3-teiliges Lounge-Set für den Garten. Wetterfest und UV-beständig."},
            {"name": "Yoga-Matte Premium", "price": 39.99, "category": "sport",
             "description": "Rutschfeste Yoga-Matte mit Tragegurt. 6mm dick, perfekt für Yoga und Pilates."},
            {"name": "Holzeisenbahn Set 100-teilig", "price": 59.99, "category": "spielzeug",
             "description": "Großes Holzeisenbahn-Set kompatibel mit allen gängigen Schienen. FSC-zertifiziert."},
            {"name": "Dashcam 4K", "price": 129.99, "category": "auto-motorrad",
             "description": "4K Dashcam mit Nachtsicht und Parkmodus. Inklusive 64GB SD-Karte."},
            {"name": "JDS Search API Zugang", "price": 9.99, "category": "software",
             "description": "API-Zugang zur JDS Search Engine. 10.000 Anfragen pro Monat inklusive."},
            {"name": "Smartwatch X200", "price": 199.99, "category": "elektronik",
             "description": "Moderne Smartwatch mit Pulsmesser, GPS und 14 Tagen Akkulaufzeit."},
            {"name": "Kochbuch: Weltküche", "price": 34.99, "category": "buecher",
             "description": "500 Rezepte aus aller Welt. Mit Schritt-für-Schritt-Anleitungen und Bildern."},
        ]
        for prod_data in products:
            cat = Category.objects.get(slug=prod_data["category"])
            Product.objects.create(
                seller=user,
                category=cat,
                name=prod_data["name"],
                price=prod_data["price"],
                description=prod_data["description"],
            )
        self.stdout.write(f"  [OK] {len(products)} Produkte erstellt")

        # Calendar + Events
        Calendar.objects.all().delete()
        cal = Calendar.objects.create(user=user, name="Mein Kalender", color="#4285f4")
        now = timezone.now()
        events = [
            {"title": "Sprint Review", "start_time": now + timedelta(days=1, hours=10 - now.hour),
             "end_time": now + timedelta(days=1, hours=11 - now.hour),
             "color": "#4285f4", "location": "Konferenzraum A"},
            {"title": "Mittagessen mit Team", "start_time": now + timedelta(days=2, hours=12 - now.hour),
             "end_time": now + timedelta(days=2, hours=13 - now.hour),
             "color": "#2ecc71", "location": "Restaurant Bella Italia"},
            {"title": "JDS Produkt-Launch", "start_time": now + timedelta(days=5),
             "end_time": now + timedelta(days=5, hours=2),
             "color": "#f39c12", "all_day": True},
            {"title": "Code Review", "start_time": now + timedelta(hours=15 - now.hour),
             "end_time": now + timedelta(hours=16 - now.hour),
             "color": "#9b59b6"},
            {"title": "Kunden-Meeting", "start_time": now + timedelta(days=3, hours=9 - now.hour),
             "end_time": now + timedelta(days=3, hours=10 - now.hour),
             "color": "#e74c3c", "location": "Online (Zoom)"},
        ]
        for ev_data in events:
            all_day = ev_data.pop("all_day", False)
            Event.objects.create(calendar=cal, all_day=all_day, **ev_data)
        self.stdout.write(f"  [OK] {len(events)} Termine erstellt")

        self.stdout.write(self.style.SUCCESS("\n=== Seed completed! ==="))
        self.stdout.write("   Run: python manage.py runserver")
        self.stdout.write("   Login: JoelDigitals / Jo240207!")
