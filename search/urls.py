from django.urls import path
from . import views

urlpatterns = [
    path("", views.search_home, name="search_home"),
    path("autocomplete/", views.autocomplete, name="search_autocomplete"),
    path("history/", views.history_view, name="search_history"),
    path("history/delete/<int:pk>/", views.history_delete, name="history_delete"),
    path("admin/", views.admin_index, name="search_admin"),
    path("admin/delete/<int:pk>/", views.delete_index, name="search_delete"),
    path("verify/", views.verify_domain, name="verify_domain"),
    path("verify/<int:pk>/", views.verify_check, name="verify_check"),
    path("ads/", views.ads_home, name="ads_home"),
    path("ads/create/", views.ads_create, name="ads_create"),
    path("ads/click/<int:ad_id>/", views.ad_click, name="ad_click"),
    path("wallet/topup/", views.wallet_topup, name="wallet_topup"),
    path("wallet/stripe/", views.stripe_checkout, name="stripe_checkout"),
    path("maps/", views.maps_view, name="maps_view"),
    path("privacy/", views.privacy_view, name="privacy"),
    path("dns-guide/", views.dns_guide, name="dns_guide"),
    path("sitemap.xml", views.sitemap_view, name="sitemap"),
]
