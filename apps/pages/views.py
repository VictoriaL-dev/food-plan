from django.shortcuts import render


def index(request):
    return render(request, "index.html")


def card1(request):
    context = {"is_card": True}
    return render(request, "card1.html", context)


def card2(request):
    context = {"is_card": True}
    return render(request, "card2.html", context)


def card3(request):
    context = {"is_card": True}
    return render(request, "card3.html", context)


def make_order(request):
    context = {"is_order": True}
    return render(request, "order.html", context)


def show_profile(request):
    return render(request, "lk.html")


def login(request):
    context = {"is_login": True}
    return render(request, "auth.html", context)


def register(request):
    context = {"is_registration": True}
    return render(request, "registration.html", context)
