from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
from .models import Category, Product, Cart, CartItem


def marketplace_home(request):
    query = request.GET.get("q", "")
    category_slug = request.GET.get("cat", "")

    products = Product.objects.filter(is_active=True)
    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
    if category_slug:
        products = products.filter(category__slug=category_slug)

    categories = Category.objects.all()
    cart_count = 0
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart_count = cart.count()

    return render(
        request,
        "marketplace/marketplace.html",
        {
            "products": products,
            "categories": categories,
            "query": query,
            "active_category": category_slug,
            "cart_count": cart_count,
        },
    )


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    cart_count = 0
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart_count = cart.count()
    return render(
        request,
        "marketplace/product_detail.html",
        {"product": product, "cart_count": cart_count},
    )


@login_required
def product_create(request):
    categories = Category.objects.all()
    if request.method == "POST":
        category = None
        if request.POST.get("category"):
            category = get_object_or_404(Category, id=request.POST["category"])
        Product.objects.create(
            seller=request.user,
            category=category,
            name=request.POST.get("name"),
            description=request.POST.get("description", ""),
            price=request.POST.get("price"),
            image_url=request.POST.get("image_url", ""),
        )
        return redirect("marketplace_home")
    return render(request, "marketplace/product_form.html", {"categories": categories})


@login_required
def cart_view(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    return render(request, "marketplace/cart.html", {"cart": cart})


@login_required
def cart_add(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    cart, _ = Cart.objects.get_or_create(user=request.user)
    item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        item.quantity += 1
        item.save()
    messages.success(request, f'"{product.name}" zum Warenkorb hinzugefügt.')
    return redirect("cart_view")


@login_required
def cart_update(request, item_id):
    item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
    if request.method == "POST":
        qty = int(request.POST.get("quantity", 1))
        if qty > 0:
            item.quantity = qty
            item.save()
        else:
            item.delete()
    return redirect("cart_view")


@login_required
def cart_remove(request, item_id):
    item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
    item.delete()
    return redirect("cart_view")
