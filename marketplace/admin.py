from django.contrib import admin
from .models import Category, Product, Cart, CartItem, CloudFile


@admin.register(CloudFile)
class CloudFileAdmin(admin.ModelAdmin):
    list_display = ["name", "user", "size", "content_type", "created_at"]
    search_fields = ["name"]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "price", "seller", "category", "is_active", "created_at"]
    list_filter = ["is_active", "category"]
    search_fields = ["name", "description"]


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "created_at", "total"]
    inlines = [CartItemInline]
