from django.shortcuts import render, redirect
from .models import Review


def index(request):
    return render(request, "index.html")


def make_order(request):
    context = {"is_order": True}
    return render(request, "order.html", context)


def reviews_view(request):
    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect("pages:reviews")

        user_name = request.POST.get("user_name")
        text = request.POST.get("text")
        rating = request.POST.get("rating")
        if user_name and text and rating:
            Review.objects.create(
                user_name=user_name, text=text, rating=int(rating)
            )
            return redirect("pages:reviews")

    reviews = Review.objects.all().order_by("-created_at")
    return render(request, "reviews.html", {"reviews": reviews})