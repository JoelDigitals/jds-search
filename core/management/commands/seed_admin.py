from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = "Erstellt nur den Admin-User (keine Testdaten)"

    def handle(self, *args, **kwargs):
        if not User.objects.filter(username="JoelDigitals").exists():
            User.objects.create_superuser("JoelDigitals", "admin@jds-search.de", "Jo240207!")
            self.stdout.write(self.style.SUCCESS("[OK] Admin 'JoelDigitals' erstellt"))
        else:
            self.stdout.write("  Admin existiert bereits")
        self.stdout.write("  python manage.py runserver -> http://localhost:8000")
