from django.shortcuts import render
from django.db.models import Count
from search.models import SearchIndex, SearchQuery
from mail_app.models import Email
from planner.models import Event
from marketplace.models import Product
from jdai.models import ChatSession
from datetime import date, timedelta


def insights_home(request):
    stats = {
        "pages": SearchIndex.objects.count(),
        "categories": SearchIndex.objects.values("category").annotate(n=Count("id")).order_by("-n")[:10],
        "mails": Email.objects.count(),
        "events": Event.objects.count(),
        "products": Product.objects.count(),
        "chats": ChatSession.objects.count(),
        "searches_today": SearchQuery.objects.filter(searched_at__gte=date.today()).count(),
        "searches_total": SearchQuery.objects.count(),
    }

    labels = []
    counts = []
    for i in range(7, 0, -1):
        d = date.today() - timedelta(days=i)
        labels.append(d.strftime("%a"))
        counts.append(SearchQuery.objects.filter(searched_at__date=d).count())

    return render(request, "insights/insights.html", {
        "stats": stats,
        "chart_labels": labels,
        "chart_data": counts,
    })
