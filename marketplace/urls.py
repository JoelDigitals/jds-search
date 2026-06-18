from django.urls import path
from . import views

urlpatterns = [
    path("", views.marketplace_home, name="marketplace_home"),
    path("product/<int:pk>/", views.product_detail, name="product_detail"),
    path("create/", views.product_create, name="product_create"),
    path("cart/", views.cart_view, name="cart_view"),
    path("cart/add/<int:product_id>/", views.cart_add, name="cart_add"),
    path("cart/update/<int:item_id>/", views.cart_update, name="cart_update"),
    path("cart/remove/<int:item_id>/", views.cart_remove, name="cart_remove"),
]
