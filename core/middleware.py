from django.conf import settings


SUBDOMAIN_CONFIG = {
    "main": {"name": "JDS Search", "template": "core/landing.html", "url_name": "landing"},
    "search": {"name": "JDS Search", "template": "core/landing.html", "url_name": "landing"},
    "mail": {"name": "JDS Mail", "template": "mail_app/mail_subdomain.html", "url_name": "mail_home"},
    "planner": {"name": "JDS Planer", "template": "planner/planner.html", "url_name": "planner_home"},
    "marketplace": {"name": "JDS Marketplace", "template": "marketplace/marketplace.html", "url_name": "marketplace_home"},
    "jdai": {"name": "JDAI", "template": "jdai/chat_subdomain.html", "url_name": "jdai_home"},
    "insights": {"name": "JDS Insights", "template": "insights/insights.html", "url_name": "insights_home"},
    "present": {"name": "JDS Present", "template": "present/present_home.html", "url_name": "present_home"},
    "translate": {"name": "JDS Translate", "template": "core/translate.html", "url_name": "translate"},
    "news": {"name": "JDS News", "template": "core/news.html", "url_name": "news"},
    "notes": {"name": "JDS Notizen", "template": "notes/notes.html", "url_name": "notes_home"},
    "maps": {"name": "JDS Maps", "template": "search/maps.html", "url_name": "maps_view"},
    "ads": {"name": "JDS Ads", "template": "search/ads.html", "url_name": "ads_home"},
    "api": {"name": "JDS API", "template": "api/docs.html", "url_name": "api_docs"},
}


def get_subdomain(host):
    host = host.lower().split(":")[0]
    for known in ["lvh.me", "jds-search.de"]:
        if host == known:
            return "main"
        if host.endswith("." + known):
            return host[: -len("." + known)]
    if host in ("localhost", "127.0.0.1"):
        return "main"
    parts = host.split(".")
    return parts[0] if len(parts) > 1 else "main"


class SubdomainRoutingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host().split(":")[0]
        subdomain = get_subdomain(host)

        request.jds_subdomain = subdomain
        request.jds_subdomain_config = SUBDOMAIN_CONFIG.get(subdomain, SUBDOMAIN_CONFIG["main"])

        if subdomain not in ("main", "www") and subdomain in SUBDOMAIN_CONFIG:
            config = SUBDOMAIN_CONFIG[subdomain]
            request.jds_sub_only = True
            request.jds_sub_name = config["name"]
        else:
            request.jds_sub_only = False
            request.jds_sub_name = "JDS"

        return self.get_response(request)
