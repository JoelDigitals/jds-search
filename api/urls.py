from django.urls import path
from . import views

urlpatterns = [
    path("", views.api_docs, name="api_docs"),
    path("v1/search/", views.search_api, name="api_search"),
    path("v1/search/stats/", views.search_stats_api, name="api_search_stats"),
    path("v1/mail/inbox/", views.mail_inbox_api, name="api_mail_inbox"),
    path("v1/mail/send/", views.mail_send_api, name="api_mail_send"),
    path("v1/calendar/events/", views.calendar_api, name="api_calendar"),
    path("v1/marketplace/products/", views.marketplace_api, name="api_marketplace"),
    path("v1/user/profile/", views.user_profile_api, name="api_user_profile"),
]
