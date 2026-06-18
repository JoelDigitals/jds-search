from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from mail_app.models import Email
import imaplib
import email as emaillib
from email.policy import default
from email.utils import parseaddr
import time


class Command(BaseCommand):
    help = "Holt externe Mails per IMAP ab und stellt sie JDS-Nutzern zu"

    def add_arguments(self, parser):
        parser.add_argument("--host", default="imap.gmail.com")
        parser.add_argument("--user", required=True)
        parser.add_argument("--password", required=True)
        parser.add_argument("--interval", type=int, default=60)
        parser.add_argument("--once", action="store_true")

    def handle(self, *args, **options):
        host = options["host"]
        username = options["user"]
        password = options["password"]
        interval = options["interval"]

        while True:
            try:
                mail = imaplib.IMAP4_SSL(host)
                mail.login(username, password)
                mail.select("INBOX")
                _, data = mail.search(None, "UNSEEN")
                ids = data[0].split()
                imported = 0

                for mid in ids:
                    _, msg_data = mail.fetch(mid, "(RFC822)")
                    raw = msg_data[0][1]
                    msg = emaillib.message_from_bytes(raw, policy=default)
                    sender = parseaddr(msg["From"])[1] or msg["From"]
                    to_all = msg.get_all("To", []) + msg.get_all("Cc", [])
                    subject = msg.get("Subject", "Kein Betreff")
                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain":
                                body = part.get_content()
                                break
                    else:
                        body = msg.get_content()
                    if not isinstance(body, str):
                        body = str(body)

                    for addr in to_all:
                        _, recipient = parseaddr(addr)
                        if recipient and recipient.endswith("@jds-search.de"):
                            local = recipient.split("@")[0].lower()
                            user = User.objects.filter(username__iexact=local).first()
                            if user:
                                Email.objects.create(
                                    user=user, sender=sender, recipient=recipient,
                                    subject=subject or "Kein Betreff", body=body or "", folder="inbox",
                                )
                                imported += 1

                mail.logout()
                if imported:
                    self.stdout.write(f"[OK] {imported} Mails zugestellt")
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"[ERR] {e}"))
            if options["once"]:
                break
            time.sleep(interval)
