from django.urls import path
from . import views

urlpatterns = [
    path("", views.mail_home, name="mail_home"),
    path("folder/<str:folder>/", views.mail_home, name="mail_folder"),
    path("compose/", views.compose, name="mail_compose"),
    path("detail/<int:pk>/", views.mail_detail, name="mail_detail"),
    path("action/<int:pk>/<str:action>/", views.mail_action, name="mail_action"),
    path("webhook/", views.mail_webhook, name="mail_webhook"),
]
