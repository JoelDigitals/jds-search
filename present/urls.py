from django.urls import path
from . import views

urlpatterns = [
    path("", views.present_home, name="present_home"),
    path("my/", views.my_profile, name="my_profile"),
    path("<str:username>/", views.profile_view, name="present_profile"),
]
