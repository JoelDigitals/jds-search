from django.urls import path
from . import views

urlpatterns = [
    path("", views.chat_home, name="jdai_home"),
    path("new/", views.new_chat, name="jdai_new"),
    path("send/<int:session_id>/", views.send_message, name="jdai_send"),
    path("send-anonymous/", views.send_anonymous, name="jdai_send_anonymous"),
    path("delete/<int:session_id>/", views.delete_chat, name="jdai_delete"),
]
