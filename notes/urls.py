from django.urls import path
from . import views

urlpatterns = [
    path("", views.notes_home, name="notes_home"),
    path("create/", views.note_create, name="note_create"),
    path("update/<int:pk>/", views.note_update, name="note_update"),
    path("delete/<int:pk>/", views.note_delete, name="note_delete"),
    path("pin/<int:pk>/", views.note_pin, name="note_pin"),
    path("archive/<int:pk>/", views.note_archive, name="note_archive"),
]
