from django.urls import path
from . import views

urlpatterns = [
    path("", views.planner_home, name="planner_home"),
    path("create/", views.event_create, name="event_create"),
    path("delete/<int:pk>/", views.event_delete, name="event_delete"),
]
