from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib import messages


def landing(request):
    return render(request, "core/landing.html")


def login_view(request):
    if request.method == "POST":
        login_id = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        next_url = request.POST.get("next", request.GET.get("next", "search_home"))

        user = authenticate(request, username=login_id, password=password)
        if user is None and "@" in login_id:
            from django.contrib.auth.models import User
            u = User.objects.filter(email=login_id).first()
            if u:
                user = authenticate(request, username=u.username, password=password)

        if user is not None:
            login(request, user)
            return redirect(next_url)
        else:
            return render(request, "core/login.html", {"error": "Ungultige Anmeldedaten.", "login_id": login_id, "next": next_url})

    return render(request, "core/login.html", {"next": request.GET.get("next", "")})


def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email_local = request.POST.get("email_local", "").strip().lower()
        password1 = request.POST.get("password1", "")
        password2 = request.POST.get("password2", "")

        errors = []
        if not username or len(username) < 3:
            errors.append("Benutzername muss mindestens 3 Zeichen lang sein.")
        if User.objects.filter(username=username).exists():
            errors.append("Benutzername bereits vergeben.")
        if not email_local:
            email_local = username.lower()
        if " " in email_local or "@" in email_local:
            errors.append("E-Mail-Teil darf keine Leerzeichen oder @ enthalten.")
        if password1 != password2:
            errors.append("Passwoerter stimmen nicht ueberein.")
        if len(password1) < 5:
            errors.append("Passwort muss mindestens 5 Zeichen lang sein.")

        if errors:
            return render(request, "core/register.html", {"errors": errors, "username": username, "email_local": email_local})

        user = User.objects.create_user(username=username, password=password1)
        user.email = f"{email_local}@jds-search.de"
        user.save()

        from mail_app.models import UserEmail
        UserEmail.objects.get_or_create(user=user, defaults={"address": f"{email_local}@jds-search.de"})

        login(request, user)
        return redirect("search_home")

    return render(request, "core/register.html")


def logout_view(request):
    logout(request)
    return redirect("landing")


def home(request):
    return redirect("landing")


def translate_view(request):
    return render(request, "core/translate.html")


def news_view(request):
    articles = [
        {"title": "JDS Crawler indexiert das Web", "source": "JDS Tech Blog", "time": "vor 2h",
         "snippet": "Der neue JDS Crawler indexiert jetzt Webseiten in Echtzeit mit verbesserter Erkennung.", "url": "#"},
        {"title": "JDAI bekommt Sprachmodell-Update", "source": "JDS AI Labs", "time": "vor 5h",
         "snippet": "Der KI-Assistent JDAI wurde mit neuen Antwort-Mustern und besserer Kontexterkennung ausgestattet.", "url": "#"},
        {"title": "JDS Mail: Ende-zu-Ende Verschlüsselung aktiv", "source": "JDS Security", "time": "vor 8h",
         "snippet": "Ab sofort werden alle E-Mails mit TLS 1.3 verschlüsselt. DSGVO-konform.", "url": "#"},
        {"title": "Supabase PostgreSQL: JDS migriert Datenbank", "source": "JDS Engineering", "time": "vor 1d",
         "snippet": "Die Migration zu Supabase PostgreSQL ist abgeschlossen. Schnellere Suchanfragen.", "url": "#"},
    ]
    return render(request, "core/news.html", {"articles": articles})


def profile_view(request):
    from search.models import SearchQuery
    from mail_app.models import Email
    from planner.models import Event
    from jdai.models import ChatSession
    from api.models import APIKey

    api_keys = []
    search_count = mail_count = event_count = chat_count = 0

    if request.user.is_authenticated:
        api_keys = APIKey.objects.filter(user=request.user, is_active=True)

        if request.method == "POST":
            email = request.POST.get("email", "").strip()
            password = request.POST.get("password", "")
            user = request.user
            if email:
                user.email = email
            if password and len(password) >= 5:
                user.set_password(password)
                update_session_auth_hash(request, user)
            user.save()

        search_count = SearchQuery.objects.filter(user=request.user).count()
        mail_count = Email.objects.filter(user=request.user).count()
        event_count = Event.objects.filter(calendar__user=request.user).count()
        chat_count = ChatSession.objects.filter(user=request.user).count()

    return render(request, "core/profile.html", {
        "api_keys": api_keys,
        "search_count": search_count,
        "mail_count": mail_count,
        "event_count": event_count,
        "chat_count": chat_count,
    })


def developer_view(request):
    from api.models import APIKey
    api_keys = []
    if request.user.is_authenticated:
        api_keys = APIKey.objects.filter(user=request.user, is_active=True)

        if request.method == "POST":
            action = request.POST.get("action")
            if action == "create_key":
                name = request.POST.get("key_name", "API Key")
                key, key_hash, prefix = APIKey.generate()
                APIKey.objects.create(user=request.user, name=name, key_hash=key_hash, prefix=prefix)
                return render(request, "core/developer.html", {
                    "api_keys": APIKey.objects.filter(user=request.user, is_active=True),
                    "new_key": key,
                    "new_prefix": prefix,
                })

    return render(request, "core/developer.html", {"api_keys": api_keys})
