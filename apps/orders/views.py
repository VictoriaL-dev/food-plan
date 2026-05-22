from django.views import View
from django.db import transaction
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import OrderForm
from apps.menu.models import Menu
from .models import Order, PromoCode


class CheckPromoCodeView(View):
    """API для проверки промокода."""

    def get(self, request):
        code = request.GET.get("code", "").strip()
        if not code:
            return JsonResponse({"is_valid": False, "discount": 0})

        promo = PromoCode.objects.filter(code=code).first()

        if not promo or not promo.is_valid():
            return JsonResponse({"is_valid": False, "discount": 0, "error": "Неверный или просроченный промокод."})

        if request.user.is_authenticated:
            already_used = Order.objects.filter(user=request.user, promocode=promo).exists()
            if already_used:
                return JsonResponse({"is_valid": False, "discount": 0, "error": "Вы уже использовали этот промокод."})

        return JsonResponse({"is_valid": True, "discount": promo.discount})


class CreateOrderView(LoginRequiredMixin, View):
    login_url = reverse_lazy("users:login")

    def get(self, request):
        has_active = Order.objects.filter(user=request.user, is_active=True, is_paid=True).exists()

        form = OrderForm()
        menus = Menu.objects.all()
        return render(request, "orders/order.html", {
            "form": form,
            "menus": menus,
            "has_active_subscription": has_active
        })

    def post(self, request):
        form = OrderForm(request.POST, user=request.user)

        if form.is_valid():
            with transaction.atomic():
                order = form.save(commit=False)
                order.user = request.user
                order.is_paid = True
                order.save()
                form.save_m2m()
            return redirect("users:profile")

        has_active = Order.objects.filter(user=request.user, is_active=True, is_paid=True).exists()
        menus = Menu.objects.all()
        return render(request, "orders/order.html", {
            "form": form,
            "menus": menus,
            "has_active_subscription": has_active
        })
