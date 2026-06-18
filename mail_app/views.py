from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import Email


@login_required
def mail_home(request, folder="inbox"):
    folders = [
        ("inbox", "Posteingang"),
        ("sent", "Gesendet"),
        ("draft", "Entwurfe"),
        ("spam", "Spam"),
        ("archive", "Archiv"),
        ("trash", "Papierkorb"),
    ]
    category = request.GET.get("cat", "")
    emails = Email.objects.filter(user=request.user, folder=folder)
    if category:
        emails = emails.filter(subject__icontains=category)

    unread_count = Email.objects.filter(user=request.user, folder="inbox", is_read=False).count()
    template = "mail_app/mail_subdomain.html" if getattr(request, "jds_sub_only", False) else "mail_app/mail.html"

    categories = Email.objects.filter(user=request.user).values_list("subject", flat=True).distinct()[:20]
    return render(request, template, {
        "emails": emails, "folders": folders,
        "current_folder": folder, "unread_count": unread_count,
        "categories": categories, "cat": category,
    })


@login_required
def compose(request):
    if request.method == "POST":
        recipient = request.POST.get("to", "")
        subject = request.POST.get("subject", "")
        body = request.POST.get("body", "")
        sender = f"{request.user.username}@jds-search.de"

        Email.objects.create(
            user=request.user, sender=sender,
            recipient=recipient, subject=subject,
            body=body, folder="sent",
        )

        try:
            send_mail(
                subject=subject,
                message=body,
                from_email=sender,
                recipient_list=[recipient],
                fail_silently=True,
            )
            messages.success(request, f"E-Mail an {recipient} gesendet.")
        except Exception:
            messages.warning(request, "E-Mail gespeichert, SMTP-Versand fehlgeschlagen.")

        return redirect("mail_home")

    return render(request, "mail_app/compose.html")


@login_required
def mail_detail(request, pk):
    email = get_object_or_404(Email, pk=pk, user=request.user)
    email.is_read = True
    email.save()
    return render(request, "mail_app/detail.html", {"email": email})


@login_required
def mail_action(request, pk, action):
    email = get_object_or_404(Email, pk=pk, user=request.user)
    if action == "trash":
        email.folder = "trash"
    elif action == "archive":
        email.folder = "archive"
    elif action == "spam":
        email.folder = "spam"
    elif action == "star":
        email.is_starred = not email.is_starred
    email.save()
    if action == "star":
        return redirect(request.META.get("HTTP_REFERER", "/mail/"))
    return redirect("mail_home")
