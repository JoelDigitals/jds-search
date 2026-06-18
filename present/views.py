from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import BusinessProfile, BusinessService, BusinessReview


def present_home(request):
    profiles = BusinessProfile.objects.filter(is_published=True)[:20]
    return render(request, "present/present_home.html", {"profiles": profiles})


@login_required
def my_profile(request):
    try:
        profile = BusinessProfile.objects.get(user=request.user)
    except BusinessProfile.DoesNotExist:
        profile = None

    if request.method == "POST":
        defaults = {
            "business_name": request.POST.get("business_name"),
            "slogan": request.POST.get("slogan", ""),
            "description": request.POST.get("description", ""),
            "logo_url": request.POST.get("logo_url", ""),
            "website": request.POST.get("website", ""),
            "phone": request.POST.get("phone", ""),
            "email": request.POST.get("email", ""),
            "address": request.POST.get("address", ""),
            "latitude": request.POST.get("latitude") or None,
            "longitude": request.POST.get("longitude") or None,
            "service_area": request.POST.get("service_area", ""),
            "opening_hours": request.POST.get("opening_hours", ""),
            "special_hours": request.POST.get("special_hours", ""),
            "category": request.POST.get("category", ""),
            "inquiry_url": request.POST.get("inquiry_url", ""),
            "tags": request.POST.get("tags", ""),
            "is_published": request.POST.get("is_published") == "on",
        }
        profile, _ = BusinessProfile.objects.update_or_create(
            user=request.user, defaults=defaults
        )
        return redirect("present_profile", username=request.user.username)

    services = profile.services.all() if profile else []
    reviews = profile.reviews.all() if profile else []
    categories = ["Restaurant", "Arzt", "Handwerker", "Anwalt", "Friseur", "Fitness", "Hotel", "Shop", "Berater", "Agentur", "Software", "Marketing", "Sonstiges"]
    return render(
        request,
        "present/my_profile.html",
        {"profile": profile, "services": services, "reviews": reviews, "categories": categories},
    )


def profile_view(request, username):
    profile = get_object_or_404(BusinessProfile, user__username=username, is_published=True)
    services = profile.services.all()
    reviews = profile.reviews.all()
    tag_list = [t.strip() for t in profile.tags.replace(",", " ").split() if t.strip()] if profile.tags else []

    if request.method == "POST" and request.user.is_authenticated:
        rating = int(request.POST.get("rating", 0))
        comment = request.POST.get("comment", "").strip()
        if 1 <= rating <= 5 and comment:
            BusinessReview.objects.create(profile=profile, author=request.user, rating=rating, comment=comment)
            return redirect("present_profile", username=username)

    return render(
        request,
        "present/profile_detail.html",
        {"profile": profile, "services": services, "reviews": reviews, "tag_list": tag_list},
    )
