from django.conf import settings


def jds_domain(request):
    host = request.get_host().split(":")[0]
    port = request.get_port()
    scheme = "https" if request.is_secure() else "http"

    # Detect base domain from current host
    from core.middleware import get_subdomain
    subdomain = get_subdomain(host)

    if "lvh.me" in host:
        base = "lvh.me"
    elif "localhost" in host or "127.0.0.1" in host:
        base = f"localhost:{port}"
    else:
        base = settings.BASE_DOMAIN

    port_suffix = f":{port}" if port not in ("80", "443") and base == "lvh.me" else ""
    if "localhost" in base:
        port_suffix = f":{port}"

    base_url = f"{scheme}://{base}{port_suffix}" if port_suffix else f"{scheme}://{base}"

    def sub_url(sub):
        if "lvh.me" in base:
            return f"{scheme}://{sub}.lvh.me{port_suffix}"
        if "localhost" in base or "127.0.0.1" in base:
            return f"{scheme}://{base}"
        return f"{scheme}://{sub}.{base}"

    return {
        "jds_subdomain": subdomain,
        "jds_domain_root": base_url,
        "jds_url_search": sub_url("search"),
        "jds_url_mail": sub_url("mail"),
        "jds_url_planner": sub_url("planner"),
        "jds_url_marketplace": sub_url("marketplace"),
        "jds_url_jdai": sub_url("jdai"),
        "jds_url_insights": sub_url("insights"),
        "jds_url_present": sub_url("present"),
        "jds_url_translate": sub_url("translate"),
        "jds_url_news": sub_url("news"),
        "jds_url_notes": sub_url("notes"),
        "jds_url_maps": sub_url("maps"),
        "jds_url_ads": "/search/ads/",
    }
