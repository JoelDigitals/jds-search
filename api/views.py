from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.utils import timezone
from datetime import timedelta
from search.models import SearchIndex, SearchQuery
from .decorators import api_auth, json_response


def api_docs(request):
    endpoints = [
        {"method": "GET", "path": "/api/v1/search/", "desc": "Suche im Index", "params": "q, page, limit"},
        {"method": "GET", "path": "/api/v1/search/stats/", "desc": "Such-Statistiken"},
        {"method": "GET", "path": "/api/v1/mail/inbox/", "desc": "Posteingang (Auth)"},
        {"method": "POST", "path": "/api/v1/mail/send/", "desc": "E-Mail senden (Auth)"},
        {"method": "GET", "path": "/api/v1/calendar/events/", "desc": "Termine (Auth)"},
        {"method": "GET", "path": "/api/v1/marketplace/products/", "desc": "Produkte"},
        {"method": "GET", "path": "/api/v1/user/profile/", "desc": "User-Profil (Auth)"},
    ]
    return render(request, "api/docs.html", {"endpoints": endpoints})


@api_auth(require_key=False)
def search_api(request):
    query = request.GET.get("q", "")
    page = int(request.GET.get("page", 1))
    limit = min(int(request.GET.get("limit", 10)), 50)
    offset = (page - 1) * limit

    results = []
    total = 0
    if query:
        qs = SearchIndex.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query) | Q(content__icontains=query)
        )
        total = qs.count()
        results = list(qs[offset:offset + limit].values("id", "url", "title", "description", "category", "indexed_at"))

    SearchQuery.objects.create(
        query=query,
        ip_address=request.META.get("REMOTE_ADDR", ""),
        results_count=total,
    )

    return json_response({
        "query": query,
        "page": page,
        "total": total,
        "results": results,
    })


@api_auth(require_key=False)
def search_stats_api(request):
    stats = {
        "total_indexed": SearchIndex.objects.count(),
        "today_indexed": SearchIndex.objects.filter(indexed_at__gte=timezone.now() - timedelta(days=1)).count(),
        "categories": list(
            SearchIndex.objects.values("category").annotate(count=Count("id")).order_by("-count")[:20]
        ),
        "recent_searches": list(
            SearchQuery.objects.order_by("-searched_at")[:10].values("query", "results_count", "searched_at")
        ),
    }
    return json_response(stats)


@api_auth(require_key=True)
def mail_inbox_api(request):
    from mail_app.models import Email
    folder = request.GET.get("folder", "inbox")
    mails = Email.objects.filter(user=request.api_key.user, folder=folder).order_by("-created_at")[:50]
    return json_response({
        "folder": folder,
        "count": mails.count(),
        "messages": list(mails.values("id", "sender", "recipient", "subject", "folder", "is_read", "created_at")),
    })


@api_auth(require_key=True)
def mail_send_api(request):
    if request.method != "POST":
        return json_response({"error": "POST required"}, 405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        data = request.POST

    from mail_app.models import Email

    Email.objects.create(
        user=request.api_key.user,
        sender=f"{request.api_key.user.username}@jds-mail.de",
        recipient=data.get("to", ""),
        subject=data.get("subject", "Kein Betreff"),
        body=data.get("body", ""),
        folder="sent",
    )

    return json_response({"status": "sent"})


@api_auth(require_key=True)
def calendar_api(request):
    from planner.models import Event
    events = Event.objects.filter(calendar__user=request.api_key.user).order_by("start_time")[:50]
    return json_response({
        "count": events.count(),
        "events": list(events.values("id", "title", "description", "location", "start_time", "end_time", "color")),
    })


@api_auth(require_key=False)
def marketplace_api(request):
    from marketplace.models import Product, Category
    query = request.GET.get("q", "")
    products = Product.objects.filter(is_active=True)
    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))

    return json_response({
        "products": list(products[:50].values("id", "name", "price", "category__name", "created_at")),
        "categories": list(Category.objects.values("id", "name", "slug")),
    })


@api_auth(require_key=True)
def user_profile_api(request):
    user = request.api_key.user
    return json_response({
        "username": user.username,
        "email": f"{user.username}@jds-mail.de",
        "date_joined": user.date_joined.isoformat(),
        "api_keys": list(user.api_keys.filter(is_active=True).values("name", "prefix", "request_count", "last_used")),
    })
