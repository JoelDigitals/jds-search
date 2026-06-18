from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from mail_app.models import Email
from email.utils import parseaddr
import email as emaillib
from email.policy import default
import imaplib
import time


class Command(BaseCommand):
    help = "IMAP-Mail-Poller – dauerhaft laufen lassen"

    def add_arguments(self, parser):
        parser.add_argument("--host", default="imap.gmail.com")
        parser.add_argument("--user", required=True, help="Gmail-Adresse fur Catch-All")
        parser.add_argument("--password", required=True, help="Gmail App-Passwort (16 Zeichen)")
        parser.add_argument("--interval", type=int, default=30)

    def handle(self, *args, **opt):
        self.stdout.write("JDS Mail-Poller gestartet. Stoppen mit Strg+C.")
        while True:
            try:
                m = imaplib.IMAP4_SSL(opt["host"])
                m.login(opt["user"], opt["password"])
                m.select("INBOX")
                _, d = m.search(None, "UNSEEN")
                count = 0
                for mid in d[0].split():
                    _, raw = m.fetch(mid, "(RFC822)")
                    msg = emaillib.message_from_bytes(raw[0][1], policy=default)
                    sender = parseaddr(msg["From"])[1] or msg["From"]
                    subject = msg.get("Subject", "") or "Kein Betreff"

                    body = ""
                    if msg.is_multipart():
                        for p in msg.walk():
                            if p.get_content_type() == "text/plain":
                                body = str(p.get_content())
                                break
                    else:
                        body = str(msg.get_content())

                    for addr in (msg.get_all("To", []) + msg.get_all("Cc", [])):
                        _, rcpt = parseaddr(addr)
                        if rcpt and rcpt.endswith("@jds-search.de"):
                            user = User.objects.filter(username__iexact=rcpt.split("@")[0]).first()
                            if user:
                                Email.objects.create(user=user, sender=sender, recipient=rcpt, subject=subject, body=body, folder="inbox")
                                count += 1

                m.logout()
                if count:
                    self.stdout.write(f"  {count} neue Mail(s) zugestellt")
            except Exception as e:
                self.stdout.write(f"  [Fehler] {e}")
            time.sleep(opt["interval"])
