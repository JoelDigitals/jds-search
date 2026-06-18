from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseRedirect
from django.db.models import Q, Count, F
from django.utils import timezone
from .models import SearchIndex, SearchQuery, AdCampaign, DomainVerification, CrawlQueue, Wallet
from present.models import BusinessProfile
import re


def generate_search_answer(query, results):
    if not results or not query:
        return None
    q = query.lower().strip()
    best = results[0]
    title = (best.title or "").lower()
    desc = (best.description or "")
    domain = best.domain or ""

    if "wikipedia" in domain:
        return desc[:300] + ("..." if len(desc) > 300 else "")
    if len(q) < 4:
        return None
    if q in title:
        return f"{best.title}: {desc[:200]}"
    if any(w in title for w in q.split() if len(w) > 3):
        return f"Relevantes Ergebnis von {domain}: {best.title} – {desc[:200]}"
    return f"Top-Ergebnis fur '{query}': {best.title} ({domain})"


def get_client_ip(request):
    x = request.META.get("HTTP_X_FORWARDED_FOR")
    return x.split(",")[0].strip() if x else request.META.get("REMOTE_ADDR", "")


def score_result(result, query_lower, query_words):
    score = 0
    title_lower = (result.title or "").lower()
    desc_lower = (result.description or "").lower()
    content_lower = (result.content or "")[:2000].lower()

    if query_lower == title_lower:
        score += 100
    elif query_lower in title_lower:
        score += 50

    for word in query_words:
        if len(word) < 2:
            continue
        if word in title_lower:
            score += 8
        if word in desc_lower:
            score += 3
        if word in content_lower:
            score += 1

    if result.is_verified:
        score += 15
    if result.domain and "wikipedia" in result.domain:
        score += 10
    if result.domain and any(tld in result.domain for tld in [".edu", ".gov"]):
        score += 8
    if result.page_rank > 0:
        score += min(result.page_rank, 5)

    return score


def search_home(request):
    query = request.GET.get("q", "").strip()
    page = int(request.GET.get("page", 1))
    results = []
    ads = []
    total = 0
    wiki_panel = None
    ai_answer = None
    biz_profiles = []

    if query:
        query_lower = query.lower()
        query_words = [w for w in re.split(r"\s+", query_lower) if len(w) > 1]

        raw_results = SearchIndex.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query) | Q(content__icontains=query)
        )[:500]

        scored = []
        for r in raw_results:
            s = score_result(r, query_lower, query_words)
            r._score = s
            scored.append(r)
            if s > 30 and r.page_rank < 100:
                SearchIndex.objects.filter(pk=r.pk).update(page_rank=F("page_rank") + 0.1)

        scored.sort(key=lambda x: x._score, reverse=True)
        total = len(scored)
        offset = (page - 1) * 15
        results = scored[offset:offset + 15]

        wiki_panel = next((r for r in scored if r.domain and "wikipedia" in r.domain), None) or (scored[0] if scored else None)

        SearchQuery.objects.create(
            user=request.user if request.user.is_authenticated else None,
            query=query, ip_address=get_client_ip(request), results_count=total,
        )

        ads = list(AdCampaign.objects.filter(is_active=True).order_by("?")[:5])
        for ad in ads:
            AdCampaign.objects.filter(pk=ad.pk).update(impressions=F("impressions") + 1)

        ai_answer = generate_search_answer(query, results)

        biz_profiles = list(BusinessProfile.objects.filter(
            Q(business_name__icontains=query) | Q(description__icontains=query) | Q(slogan__icontains=query),
            is_published=True
        )[:5])

        results_with_ads = []
        ad_idx = 0
        for i, r in enumerate(results):
            results_with_ads.append(("result", r))
            if (i + 1) % 3 == 0 and ad_idx < len(ads):
                results_with_ads.append(("ad", ads[ad_idx]))
                ad_idx += 1

    return render(request, "search/search.html", {
        "query": query, "results": results_with_ads if query else [], "ads": ads,
        "total": total, "page": page, "has_next": total > page * 15,
        "wiki_panel": wiki_panel, "ai_answer": ai_answer,
        "biz_profiles": biz_profiles,
    })


def ad_click(request, ad_id):
    ad = get_object_or_404(AdCampaign, pk=ad_id, is_active=True)
    if ad.remaining_budget() < ad.cost_per_click:
        ad.is_active = False
        ad.save()
        return redirect(ad.target_url)
    ad.clicks = F("clicks") + 1
    ad.save(update_fields=["clicks"])
    ad.refresh_from_db()
    if ad.remaining_budget() <= 0:
        ad.is_active = False
        ad.save(update_fields=["is_active"])
    return HttpResponseRedirect(ad.target_url)


def autocomplete(request):
    q = request.GET.get("q", "")
    if len(q) < 2:
        return JsonResponse({"suggestions": []})
    suggestions = list(SearchIndex.objects.filter(
        Q(title__icontains=q) | Q(description__icontains=q)
    ).values_list("title", flat=True)[:8])
    return JsonResponse({"suggestions": suggestions})


@login_required
def history_view(request):
    history = SearchQuery.objects.filter(user=request.user)[:50]
    return render(request, "search/history.html", {"history": history})


@login_required
def history_delete(request, pk):
    sq = get_object_or_404(SearchQuery, pk=pk, user=request.user)
    sq.delete()
    return redirect("search_history")


# === DOMAIN VERIFICATION ===
@login_required
def verify_domain(request):
    if request.method == "POST":
        domain = request.POST.get("domain", "").strip().lower()
        method = request.POST.get("method", "dns")
        if domain:
            dv, created = DomainVerification.objects.get_or_create(
                domain=domain, defaults={"owner": request.user, "method": method}
            )
            return render(request, "search/verify_detail.html", {"verification": dv})

    verifications = DomainVerification.objects.filter(owner=request.user)
    return render(request, "search/verify_list.html", {"verifications": verifications})


@login_required
def verify_check(request, pk):
    import requests
    dv = get_object_or_404(DomainVerification, pk=pk, owner=request.user)

    verified = False
    if dv.method == "dns":
        try:
            import dns.resolver
            answers = dns.resolver.resolve(dv.domain, "TXT")
            for a in answers:
                if dv.token in a.to_text():
                    verified = True
                    break
        except Exception:
            pass
    elif dv.method == "meta":
        try:
            r = requests.get(f"https://{dv.domain}", timeout=10, headers={"User-Agent": "JDS-Verify/1.0"})
            if dv.token in r.text:
                verified = True
        except Exception:
            pass
    elif dv.method == "file":
        try:
            r = requests.get(f"https://{dv.domain}/jds-verify-{dv.token[:12]}.html", timeout=10, headers={"User-Agent": "JDS-Verify/1.0"})
            if dv.token in r.text:
                verified = True
        except Exception:
            pass

    if verified:
        dv.status = "verified"
        dv.verified_at = timezone.now()
        dv.save()

    return render(request, "search/verify_detail.html", {"verification": dv, "check_result": verified})


# === ADMIN (paginated) ===
@login_required
def admin_index(request):
    page = int(request.GET.get("page", 1))
    cat = request.GET.get("cat", "")
    q = request.GET.get("q", "")

    qs = SearchIndex.objects.all()
    if cat:
        qs = qs.filter(category=cat)
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(url__icontains=q) | Q(domain__icontains=q))

    total = qs.count()
    pages = qs.order_by("-indexed_at")[(page - 1) * 30:page * 30]
    categories = SearchIndex.objects.values("category").annotate(n=Count("id")).order_by("-n")[:20]

    if request.method == "POST":
        url = request.POST.get("url")
        SearchIndex.objects.update_or_create(url=url, defaults={
            "title": request.POST.get("title", url),
            "description": request.POST.get("description", ""),
            "content": request.POST.get("content", ""),
            "category": request.POST.get("category", "Web"),
        })
        return redirect("search_admin")

    return render(request, "search/admin.html", {
        "pages": pages, "total": total, "page": page,
        "has_next": total > page * 30, "categories": categories,
        "cat": cat, "q": q,
    })


@login_required
def delete_index(request, pk):
    get_object_or_404(SearchIndex, pk=pk).delete()
    return redirect("search_admin")


@login_required
def ads_home(request):
    campaigns = AdCampaign.objects.filter(advertiser=request.user)
    wallet = Wallet.objects.get_or_create(user=request.user)[0]
    return render(request, "search/ads.html", {"campaigns": campaigns, "wallet": wallet})


@login_required
def ads_create(request):
    from decimal import Decimal
    if request.method == "POST":
        budget = Decimal(request.POST.get("budget", 0))
        cpc = Decimal(request.POST.get("cost_per_click", "0.10"))

        wallet = Wallet.objects.get_or_create(user=request.user)[0]
        if wallet.balance < budget:
            wallet.balance += budget
            wallet.save()

        wallet.charge(budget)
        AdCampaign.objects.create(
            advertiser=request.user,
            title=request.POST["title"],
            description=request.POST["description"],
            target_url=request.POST["target_url"],
            budget=budget,
            cost_per_click=cpc,
        )
        return redirect("ads_home")

    wallet = Wallet.objects.get_or_create(user=request.user)[0]
    return render(request, "search/ads_form.html", {"wallet": wallet})


@login_required
def wallet_topup(request):
    from decimal import Decimal
    wallet = Wallet.objects.get_or_create(user=request.user)[0]
    if wallet.balance > 999999:
        wallet.balance = 100
        wallet.save()

    if request.method == "POST":
        amount = Decimal(request.POST.get("amount", "0"))
        if amount >= 10:
            wallet.balance += amount
            wallet.save()
            return render(request, "search/wallet_topup.html", {"wallet": wallet, "success": f"{amount} EUR aufgeladen!"})
        return render(request, "search/wallet_topup.html", {"wallet": wallet, "error": "Mindestbetrag: 10 EUR"})
    return render(request, "search/wallet_topup.html", {"wallet": wallet})


def stripe_checkout(request):
    from decimal import Decimal
    from django.http import JsonResponse
    wallet = Wallet.objects.get_or_create(user=request.user)[0]
    if request.method == "POST":
        amount = Decimal(request.POST.get("amount", "10"))
        wallet.balance += amount
        wallet.save()
        return JsonResponse({"success": True, "balance": str(wallet.balance)})
    return JsonResponse({"balance": str(wallet.balance)})


def maps_view(request):
    from present.models import BusinessProfile
    locations = BusinessProfile.objects.filter(is_published=True, latitude__isnull=False).values(
        "business_name", "latitude", "longitude", "category"
    )[:50]
    return render(request, "search/maps.html", {"locations": list(locations)})


def privacy_view(request):
    return render(request, "core/privacy.html")


def dns_guide(request):
    return render(request, "search/dns_guide.html")


def sitemap_view(request):
    from django.http import HttpResponse
    from django.urls import reverse
    pages = SearchIndex.objects.order_by("-indexed_at")[:1000]
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    host = request.build_absolute_uri("/").rstrip("/")
    for p in pages:
        xml += f'  <url><loc>{p.url}</loc><lastmod>{p.indexed_at.strftime("%Y-%m-%d")}</lastmod></url>\n'
    xml += f'  <url><loc>{host}</loc></url>\n'
    for name in ["search_home", "mail_home", "planner_home", "marketplace_home"]:
        xml += f'  <url><loc>{host}{reverse(name)}</loc></url>\n'
    xml += '</urlset>'
    return HttpResponse(xml, content_type="application/xml")
