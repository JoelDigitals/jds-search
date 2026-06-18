from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import ChatSession, ChatMessage


def chat_home(request):
    if request.user.is_authenticated:
        sessions = ChatSession.objects.filter(user=request.user)
        active_session = None
        if "session_id" in request.GET:
            try:
                active_session = ChatSession.objects.get(
                    id=request.GET["session_id"], user=request.user
                )
            except ChatSession.DoesNotExist:
                pass
    else:
        sessions = []
        active_session = None

    template = "jdai/chat_subdomain.html" if getattr(request, "jds_sub_only", False) else "jdai/chat.html"
    return render(
        request,
        template,
        {
            "sessions": sessions,
            "active_session": active_session,
            "is_authenticated": request.user.is_authenticated,
        },
    )


@login_required
def new_chat(request):
    session = ChatSession.objects.create(user=request.user, title="Neuer Chat")
    return redirect(f"/jdai/?session_id={session.id}")


@login_required
def send_message(request, session_id):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    session = get_object_or_404(ChatSession, id=session_id, user=request.user)
    user_content = request.POST.get("message", "")
    response_text = ""

    if user_content.strip():
        ChatMessage.objects.create(
            session=session, role="user", content=user_content
        )

        ai_response = generate_ai_response(user_content, session)
        ChatMessage.objects.create(
            session=session, role="assistant", content=ai_response
        )
        response_text = ai_response

        if session.messages.count() == 2:
            new_title = user_content[:60]
            if len(user_content) > 60:
                new_title += "..."
            session.title = new_title
            session.save()

    messages = list(session.messages.values("role", "content", "created_at"))
    return JsonResponse({"messages": messages, "session_id": session.id})


def send_anonymous(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    user_content = request.POST.get("message", "")
    if not user_content.strip():
        return JsonResponse({"error": "empty"}, status=400)

    ai_response = generate_ai_response(user_content, None)
    return JsonResponse({
        "messages": [
            {"role": "user", "content": user_content},
            {"role": "assistant", "content": ai_response},
        ]
    })


@login_required
def delete_chat(request, session_id):
    session = get_object_or_404(ChatSession, id=session_id, user=request.user)
    session.delete()
    return redirect("/jdai/")


def generate_ai_response(user_message, session=None):
    msg = user_message.lower().strip()

    # === Greetings ===
    if any(w in msg for w in ["hallo", "hi", "hey", "moin", "guten tag"]):
        return "Hallo! Ich bin JDAI, dein KI-Assistent von Joel Digital Systems. Stelle mir eine Frage zu JDS-Diensten, Technologie oder lass dir bei Aufgaben helfen."

    # === JDS Management ===
    if any(w in msg for w in ["jds management", "management", "was macht jds"]):
        return "JDS Management ist die zentrale Verwaltungsplattform von Joel Digital Systems. Funktionen:\n\n- **Dashboard**: Ubersicht aller JDS-Dienste\n- **Nutzerverwaltung**: Accounts, Berechtigungen, SSO\n- **Domain-Verifikation**: Webseiten fur den Suchindex bestatigen\n- **Ads Manager**: Werbekampagnen mit Budget-Steuerung\n- **Wallet**: Guthaben-System fur Werbung\n- **Analytics**: Statistiken zu Suchanfragen, Index, API-Nutzung\n\nAlles erreichbar unter http://jds-search.de nach Login."

    # === JDS Search ===
    if any(w in msg for w in ["jds search", "suchmaschine", "suchen"]):
        return "JDS Search ist die integrierte Suchmaschine mit:\n\n- Indexierung echter Webseiten per Crawler\n- Intelligentem Relevanz-Ranking\n- KI-Antworten zu Suchanfragen\n- Sprachsuche und Autovervollstandigung\n- In-Page-Vorschau der Ergebnisse\n- 866+ indexierte Seiten aus Wikipedia, Tech, News"

    # === JDAI selbst ===
    if any(w in msg for w in ["jdai", "ki", "assistent", "wer bist du"]):
        return "JDAI ist der KI-Assistent von JDS. Ich helfe bei Fragen zu allen JDS-Diensten, Technologie-Themen und Alltagsaufgaben. Ich arbeite mit einer Keyword-Datenbank und lerne standig dazu."

    # === Marketplace ===
    if any(w in msg for w in ["marketplace", "marktplatz", "produkt", "verkaufen", "kaufen"]):
        return "Der JDS Marketplace bietet:\n\n- Produkte einstellen mit JDS Cloud Bild-Upload\n- Kategorien: Elektronik, Kleidung, Bucher, Sport uvm.\n- Warenkorb-System\n- Preisangaben in EUR\n- Verkaufer-Profile\n- Drag & Drop Bild-Upload direkt in die JDS Cloud"

    # === Mail ===
    if any(w in msg for w in ["mail", "email", "posteingang"]):
        return "JDS Mail ist der E-Mail-Dienst mit @jds-search.de Adressen. Features:\n\n- Posteingang, Gesendet, Entwurfe, Spam, Archiv, Papierkorb\n- Ende-zu-Ende Verschlusselung (TLS 1.3)\n- DSGVO-konform\n- Jeder Nutzer bekommt eigene @jds-search.de Adresse"

    # === Kalender ===
    if any(w in msg for w in ["kalender", "termin", "planer", "event"]):
        return "JDS Planer ist der Kalender-Dienst. Funktionen:\n\n- Monatsansicht mit Event-Farben\n- Termine mit Titel, Beschreibung, Ort\n- Ganztagige Events\n- Farbkodierung\n- Offentliche Kalenderansicht ohne Login"

    # === Preise / Kosten ===
    if any(w in msg for w in ["preis", "kosten", "gratis", "geld", "bezahlen"]):
        return "JDS-Dienste sind grundsatzlich kostenlos. Kosten entstehen nur bei:\n\n- Werbekampagnen: ab 10 EUR Budget, 0,10 EUR/Klick\n- Wallet kann per Stripe aufgeladen werden\n\nAlle anderen Dienste (Suche, Mail, Kalender, JDAI) sind gratis."

    # === Datenschutz ===
    if any(w in msg for w in ["datenschutz", "dsgvo", "sicher", "verschlusselt"]):
        return "JDS ist DSGVO-konform:\n\n- TLS 1.3 Verschlusselung fur alle Verbindungen\n- AES-256 Datenbank-Verschlusselung\n- Server in Frankfurt, Deutschland\n- Keine Tracking-Cookies\n- Recht auf Auskunft und Loschung\n- Nur technisch notwendige Session-Cookies"

    # === Technologie ===
    if any(w in msg for w in ["python", "django", "programmierung"]):
        return "JDS ist mit Django (Python) gebaut. Tech-Stack:\n\n- Backend: Django 4.2, Python 3.13\n- Frontend: Vanilla JS, iOS-Style CSS\n- Datenbank: Supabase PostgreSQL\n- Caching: Service Worker (PWA)\n- API: REST mit API-Key-Auth\n- Crawler: BeautifulSoup + Requests"

    # === Allgemein ===
    return f"Gute Frage zu: **{user_message[:80]}**\n\nAls JDAI helfe ich dir gerne weiter. Versuche es mit:\n\n- 'Was ist JDS Management?'\n- 'Wie funktioniert der Marketplace?'\n- 'Was kostet Werbung?'\n- 'Wie ist der Datenschutz?'\n\nOder nutze die [JDS Suche](/search/) fur detaillierte Ergebnisse."
