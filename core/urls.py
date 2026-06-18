from django.urls import path
from . import views

urlpatterns = [
    path("", views.landing, name="landing"),
    path("home/", views.home, name="home"),
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
    path("translate/", views.translate_view, name="translate"),
    path("news/", views.news_view, name="news"),
    path("profile/", views.profile_view, name="profile"),
    path("developer/", views.developer_view, name="developer"),
]
